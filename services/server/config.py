from pydantic import BaseModel, DirectoryPath
import tomllib
import pathlib

class ServerConfig(BaseModel):
    host: str
    port: int
    key: str

class PathsConfig(BaseModel):
    video_directory: DirectoryPath

class Config(BaseModel):
    server: ServerConfig
    paths: PathsConfig


def load_config():
    with open(pathlib.Path(__file__).parent / "config.toml", "rb") as f:
        data = tomllib.load(f)
    return Config(**data)

config = load_config()
