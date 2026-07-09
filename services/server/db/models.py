from dis import show_code

from sqlalchemy import String, Column
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Field, SQLModel, Relationship
from pydantic import model_validator, DirectoryPath, BaseModel
from typing import Optional, Annotated, Self, List, TypeAlias

from .schemas import SMB, LocalFolder, StorageMode, JobStatus

PrimaryKey = Annotated[int | None, Field(default=None, primary_key=True)]

STORAGE_REGISTRY = {
    "smb": SMB,
    "local": LocalFolder,
}

StorageType: TypeAlias = SMB | LocalFolder

class StorageConfig(SQLModel, table=True):
    id: PrimaryKey
    label: str = Field(unique=True)
    mode: str
    data: dict = Field(default_factory=dict, sa_column=Column(JSON))

    deleted_at: Optional[str] = None

    libraries: List["Library"] = Relationship(back_populates="storage")

    @property
    def config(self) -> StorageType:
        schema_class = STORAGE_REGISTRY.get(self.mode)
        if not schema_class:
            raise ValueError(f"Unknown storage mode: {self.mode}")
        return schema_class(**self.data)

    @config.setter
    def config(self, data: StorageType):
        for mode_key, schema_class in STORAGE_REGISTRY.items():
            if isinstance(data, schema_class):
                self.mode = mode_key
                self.data = data.model_dump()
                return
        raise ValueError(f"Unsupported config type: {type(data)}. Ensure it is in STORAGE_REGISTRY.")


    @model_validator(mode="after")
    def validate_payload(self) -> Self:
        schema_class = STORAGE_REGISTRY.get(self.mode)
        if not schema_class:
            raise ValueError(f"Unknown storage mode: {self.mode}")
        schema_class.model_validate(self.data)
        return self

class EncoderConfig(SQLModel, table=True):
    id: PrimaryKey
    data: str
    libraries: List["Library"] = Relationship(back_populates="encoder")
    deleted_at: Optional[str] = None

class Library(SQLModel, table=True):
    id: PrimaryKey
    label: str = Field(unique=True)
    storage_id: int = Field(default=None, foreign_key="storageconfig.id")
    storage: Optional[StorageConfig] = Relationship(back_populates="libraries")
    input_path: DirectoryPath = Field(sa_type=String)
    output_path: DirectoryPath = Field(sa_type=String)
    encoder_id: int = Field(default=None, foreign_key="encoderconfig.id")
    encoder: Optional[EncoderConfig] = Relationship(back_populates="libraries")
    sync: bool
    deleted_at: Optional[str] = None
    jobs: List["Job"] = Relationship(back_populates="library")

class Job(SQLModel, table=True):
    id: PrimaryKey
    library_id: int = Field(default=None, foreign_key="library.id")
    library: Optional[Library] = Relationship(back_populates="jobs")
    path: str
    node: Optional[str] = None
    status: JobStatus = Field(sa_type=String)
    deleted_at: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
