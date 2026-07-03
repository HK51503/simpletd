from pydantic import BaseModel

class GetJob(BaseModel):
    node: str

class FoundJob(BaseModel):
    id: int
    path: str
    encoder: dict

class CompletedDownload(BaseModel):
    node: str
    id: int

class CompletedTranscode(BaseModel):
    node: str
    id: int
    success: bool


class CompletedUpload(BaseModel):
    node: str
    id: int

class Event(BaseModel):
    event: str
    data: GetJob | FoundJob | CompletedDownload | CompletedTranscode | CompletedUpload | None
