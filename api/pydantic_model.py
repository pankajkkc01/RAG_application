from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class ModelName(str, Enum):
    GPT4_O = "gpt-4o"
    GPT4_O_MINI = "gpt-4o-mini"

class QueryInput(BaseModel):
    question: str
    session_id: str = Field(default=None)
    model: ModelName = Field(default=ModelName.GPT4_O_MINI)

class QueryResponse(BaseModel):
    answer: str
    session_id: str
    model: ModelName

class DocumentInfo(BaseModel):
    id: int
    filename: str
    upload_timestamp: datetime

class DeleteFileRequest(BaseModel):
    file_id: int

class FeedbackModel(BaseModel):
    session_id: str
    user_query: str
    model_response: str
    feedback: str  


class UserLogin(BaseModel):
    name: str
    email: str
    phone: str

from pydantic import BaseModel
from typing import List

class AllowedUser(BaseModel):
    name: str
    email: str
    phone: str

class AllowedUserList(BaseModel):
    users: List[AllowedUser]

