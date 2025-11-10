from pydantic import BaseModel
from typing import Optional, Dict, Any


class TodoItem(BaseModel):
    id: int
    task: str
    description: Optional[str] = None


class TodoResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
