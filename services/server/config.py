from pydantic import BaseModel
import tomllib

class ServerConfig(BaseModel):
    host: str
    port: int
    key: str

class PathsConfig(BaseModel):
    video_directory: str

class Config(BaseModel):
    server: ServerConfig
    paths: PathsConfig


def load_config():
    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
    return Config(**data)

config = load_config()
