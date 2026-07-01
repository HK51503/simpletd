from sqlmodel import Field, SQLModel
from typing import Optional

class Jobs(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    path: str
    node: Optional[str] = None
    status: str
    deleted_at: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

