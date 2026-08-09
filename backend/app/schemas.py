from datetime import datetime
from typing import Literal, Any
from pydantic import BaseModel, EmailStr, Field, HttpUrl, ConfigDict


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(RegisterRequest):
    pass


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    created_at: datetime


class RepositoryCreate(BaseModel):
    url: HttpUrl
    branch: str | None = None


class RepositoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner: str
    name: str
    url: str
    branch: str
    status: str
    file_count: int
    last_error: str | None
    created_at: datetime
    updated_at: datetime


AnalysisKind = Literal["ask", "bug", "code_review", "architecture", "tests", "performance"]


class AnalysisCreate(BaseModel):
    repo_id: int
    kind: AnalysisKind
    question: str = Field(min_length=3, max_length=6000)


class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    repo_id: int
    kind: str
    question: str
    status: str
    progress: int
    current_step: str
    result_json: dict[str, Any] | None
    error: str | None
    created_at: datetime
    updated_at: datetime
