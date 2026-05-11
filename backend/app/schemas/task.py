import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from app.models.task import Priority, Status


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Status = Status.todo
    priority: Priority = Priority.medium
    tags: Optional[str] = None
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        if len(v) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    tags: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskOut(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    status: Status
    priority: Priority
    tags: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    owner_id: uuid.UUID

    model_config = {"from_attributes": True}


class SearchQuery(BaseModel):
    query: str
    limit: int = 10

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Search query cannot be empty")
        return v
