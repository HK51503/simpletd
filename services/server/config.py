from pydantic import BaseModel, DirectoryPath
import tomllib
import pathlib

class ServerConfig(BaseModel):
    host: str
    port: int
    key: str

class Config(BaseModel):
    server: ServerConfig


def load_config():
    with open(pathlib.Path(__file__).parent / "config.toml", "rb") as f:
        data = tomllib.load(f)
    return Config(**data)

config = load_config()
