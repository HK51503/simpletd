import tomllib, tomli_w, socket
from pydantic import BaseModel

class ServerConfig(BaseModel):
    host: str
    port: int
    key: str

class ClientConfig(BaseModel):
    node: str
    tmp_video_directory: str

class InternalConfig(BaseModel):
    is_https: bool = False

class Config(BaseModel):
    server: ServerConfig
    client: ClientConfig
    internal: InternalConfig = InternalConfig()

def load_config():
    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
    c = Config(**data)
    if c.client.node == "":
        c.client.node = socket.gethostname()
    if c.client.tmp_video_directory == "":
        c.client.tmp_video_directory = "videos/"



    return c

def save_config(config: Config):
    with open("config.toml", "wb") as f:
        tomli_w.dump(config.model_dump(), f)

config = load_config()
