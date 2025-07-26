from dotenv import load_dotenv
load_dotenv()   # ← ensure OPENAI_API_KEY is in os.environ
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document
import os

# Initialize text splitter and embedding function

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=150, length_function=len)
# embedding_function = OpenAIEmbeddings()
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Pick the shared tokenizer encoding
encoding = tiktoken.get_encoding("cl100k_base")

# Token-aware splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    length_function=lambda txt: len(encoding.encode(txt)),
    # split on paragraphs, sentences, then words
    separators=["\n\n", "\n", ".", "!", "?", ",", " "]
)

# Use whichever embedding model you prefer
embedding_function = OpenAIEmbeddings(model="text-embedding-3-large")



# Initialize Chroma vector store
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

# Documnet Loading and splitting
def load_and_split_document(file_path: str) -> List[Document]:
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith('.html'):
        loader = UnstructuredHTMLLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    documents = loader.load()
    return text_splitter.split_documents(documents)
# document Indexing 

def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    try:   
        splits = load_and_split_document(file_path)

        # Add metadata to each split
        for split in splits:
            split.metadata['file_id'] = file_id

        vectorstore.add_documents(splits)
        return True
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False
    
 # deleting Documents
def delete_doc_from_chroma(file_id: int):
    try:
        docs = vectorstore.get(where={"file_id": file_id})
        print(f"Found {len(docs['ids'])} document chunks for file_id {file_id}")

        vectorstore._collection.delete(where={"file_id": file_id})
        print(f"Deleted all documents with file_id {file_id}")

        return True
    except Exception as e:
        print(f"Error deleting document with file_id {file_id} from Chroma: {str(e)}")
        return False

