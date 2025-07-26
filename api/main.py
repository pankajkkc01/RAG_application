import os
import shutil
import uuid
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from pydantic_model import (
    QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest,
    UserLogin, FeedbackModel, AllowedUser, AllowedUserList
)
from db_utils import (
    insert_application_logs, get_chat_history, get_all_documents,
    insert_document_record, delete_document_record,
    insert_feedback_log, insert_user_login, get_all_logged_users,
    insert_allowed_users, delete_allowed_user, list_allowed_users
)
from chroma_utils import index_document_to_chroma, delete_doc_from_chroma
from langchain_utils import get_rag_chain

# ——— Logging ———————————————————————————————————————————————————————————
logging.basicConfig(filename='app.log', level=logging.INFO)

# ——— App Init ——————————————————————————————————————————————————————————  
app = FastAPI()


# ——— 1) Chat Endpoint —————————————————————————————————————————————————————
@app.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    session_id = query_input.session_id or str(uuid.uuid4())
    logging.info(f"Session {session_id} Q: {query_input.question}")
    history   = get_chat_history(session_id)
    chain     = get_rag_chain(query_input.model.value)
    answer    = chain.invoke({"input": query_input.question, "chat_history": history})["answer"]
    insert_application_logs(session_id, query_input.question, answer, query_input.model.value)
    return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)


# ——— 2) Upload & Index Document —————————————————————————————————————————————
@app.post("/upload-doc")
def upload_and_index_document(file: UploadFile = File(...)):
    # 2a) Validate extension
    allowed = ['.pdf', '.docx', '.html']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    # 2b) Save to temp
    temp_path = f"temp_{uuid.uuid4().hex}{ext}"
    with open(temp_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    # 2c) Record in SQLite
    file_id = insert_document_record(file.filename)

    # 2d) Move to permanent storage
    os.makedirs("uploaded_docs", exist_ok=True)
    perm_path = os.path.join("uploaded_docs", file.filename)
    shutil.move(temp_path, perm_path)

    # 2e) Index into Chroma (persists internally)
    success = index_document_to_chroma(perm_path, file_id)
    if not success:
        delete_document_record(file_id)
        raise HTTPException(500, "Failed to index document.")

    return {"message": "Uploaded & indexed", "file_id": file_id}


# ——— 3) List & Delete Documents —————————————————————————————————————————————
@app.get("/list-docs", response_model=list[DocumentInfo])
def list_documents():
    return get_all_documents()

@app.post("/delete-doc")
def delete_document(request: DeleteFileRequest):
    ok1 = delete_doc_from_chroma(request.file_id)
    ok2 = delete_document_record(request.file_id)
    return {"deleted_in_chroma": ok1, "deleted_in_db": ok2}


# ——— 4) Feedback & User Logging —————————————————————————————————————————————
@app.post("/log-feedback")
def log_feedback(feedback: FeedbackModel):
    insert_feedback_log(
        feedback.session_id,
        feedback.user_query,
        feedback.model_response,
        feedback.feedback
    )
    return {"message": "Feedback logged"}

@app.post("/log-user")
def log_user(user: UserLogin):
    insert_user_login(user.name, user.email, user.phone)
    return {"message": "User login saved"}

@app.get("/list-users")
def list_users():
    return JSONResponse(content={"users": get_all_logged_users()})


# ——— 5) Allowed-Users Management ————————————————————————————————————————————
@app.post("/add-allowed-users")
def add_allowed_users(user_list: AllowedUserList):
    insert_allowed_users([u.dict() for u in user_list.users])
    return {"message": "Allowed users added"}

@app.post("/delete-allowed-user")
def remove_allowed_user(user: AllowedUser):
    delete_allowed_user(user.email)
    return {"message": f"Deleted allowed user {user.email}"}

@app.get("/list-allowed-users")
def get_allowed_users():
    return {"users": list_allowed_users()}
