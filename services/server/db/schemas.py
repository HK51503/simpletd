from pydantic import BaseModel, DirectoryPath
from enum import Enum

class SMB(BaseModel):
    server: str
    share_name: str
    user: str

class LocalFolder(BaseModel):
    path: DirectoryPath


class StorageMode(str, Enum):
    SMB = "smb"
    LOCAL = "local"

class JobStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    TRANSCODING = "transcoding"
    DOWNLOADING = "downloading"
    UPLOADING = "uploading"