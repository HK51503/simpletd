import asyncio, signal, sys
import typer
from pydantic import ValidationError
from typing import Optional


from config import Config, config, save_config
from daemon import node_client_loop

app = typer.Typer(
    no_args_is_help=True,
)




def shutdown_handler(signum, frame):
    sys.exit(0)

@app.command()
def start(
        node: Optional[str] = typer.Option(None, help="Override the node name."),
        tmp_video_directory: Optional[str] = typer.Option(None, help="Override the default tmp directory."),
):
    print("starting node")

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    if node:
        config.client.node = node
    if tmp_video_directory:
        config.client.tmp_video_directory = tmp_video_directory

    print(config)

    try:
        asyncio.run(node_client_loop(config))
    except KeyboardInterrupt:
        pass

@app.command()
def configure():
    try:
        validated_config = Config(**{"server": {
            "host": typer.prompt("Server host?"),
            "port" : typer.prompt("Server port?"),
            "key" : typer.prompt("Paste your secret key", hide_input=True),
        }})
        save_config(validated_config)
        print("Saved config successfully")
    except ValidationError as e:
        print(e)



if __name__ == "__main__":
    app()