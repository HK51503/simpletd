import tomllib, tomli_w, socket, pathlib, os
from pydantic import BaseModel, DirectoryPath, BeforeValidator
from typing import Annotated

def _expand_env_vars(value: str) -> str:
    if isinstance(value, str):
        return os.path.expandvars(value)
    return value

ExpandedDirectoryPath = Annotated[DirectoryPath, BeforeValidator(_expand_env_vars)]

class ServerConfig(BaseModel):
    host: str
    port: int
    key: str

class ClientConfig(BaseModel):
    node: str
    tmp_video_directory: ExpandedDirectoryPath

class InternalConfig(BaseModel):
    is_https: bool = False

class Config(BaseModel):
    server: ServerConfig
    client: ClientConfig
    internal: InternalConfig = InternalConfig()


def load_config():
    with open(pathlib.Path(__file__).parent / "config.toml", "rb") as f:
        data = tomllib.load(f)
    c = Config(**data)
    if c.client.node == "":
        c.client.node = socket.gethostname()
    if c.client.tmp_video_directory.as_posix() == ".":
        c.client.tmp_video_directory = pathlib.Path("videos/").expanduser()



    return c

def save_config(config: Config):
    with open(pathlib.Path(__file__).parent / "config.toml", "wb") as f:
        tomli_w.dump(config.model_dump(), f)

config = load_config()
