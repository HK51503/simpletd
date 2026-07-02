import asyncio
import json
import time
import httpx
import pathlib
import aiofiles
import ffmpeg
from ffmpeg import overwrite_output
from websockets.asyncio.client import connect, ClientConnection

from shared_protocol import Event, GetJob, CompletedDownload, CompletedTranscode, CompletedUpload

from config import Config

async def get_ws_connection(config: Config) -> ClientConnection:
    uri = f"{'wss' if config.internal.is_https else 'ws'}://{config.server.host}:{config.server.port}/ws"
    connection = await connect(uri)
    return connection

async def get_job(ws: ClientConnection, config: Config) -> Event:
    while True:
        event = Event(event="get_job", data=GetJob(node=config.client.node))
        await ws.send(event.model_dump_json())
        try:
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            received_event = Event(**json.loads(response))
            if received_event.event == "job_found":
                return received_event
            print("Job not found, trying again in 5 seconds.")
            time.sleep(5)

        except asyncio.TimeoutError:
            print("No response received within 5 seconds. Retrying...")

async def download_video(config: Config, job: Event):
    async with httpx.AsyncClient(base_url=f"{'https' if config.internal.is_https else 'http'}://{config.server.host}:{config.server.port}") as client:
        url = f"/videos/{job.data.id}"
        download_path = pathlib.Path(config.client.tmp_video_directory) / "original" / job.data.path
        download_path.parent.mkdir(exist_ok=True, parents=True)
        try:
            async with client.stream("GET", url) as response:
                response.raise_for_status()

                async with aiofiles.open(download_path, "wb") as file:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        await file.write(chunk)

                return response

        except httpx.HTTPStatusError as e:
            print(f"Error occurred, retrying in 10s: {e.response.text}({e.response.status_code})")
            time.sleep(10)

async def file_chunk_generator(file: pathlib.Path):
    async with aiofiles.open(file, "rb") as f:
        while chunk := await f.read(1024*1024):
            yield chunk

async def upload_video(config: Config, job: Event):
    async with httpx.AsyncClient(base_url=f"{'https' if config.internal.is_https else 'http'}://{config.server.host}:{config.server.port}") as client:
        url = f"/videos/{job.data.id}"
        video = pathlib.Path(config.client.tmp_video_directory) / "output" / job.data.path
        response = await client.post(url, content=file_chunk_generator(video))
        print(response)




async def transcode_video(job: Event) -> int:
    input_file = pathlib.Path(config.client.tmp_video_directory) / "original" / job.data.path
    output_file = pathlib.Path(config.client.tmp_video_directory) / "output" / job.data.path
    output_file.parent.mkdir(exist_ok=True, parents=True)
    encoder = {"vcodec": "hevc_videotoolbox", "video_bitrate": "20M", "acodec": "aac"}
    args = ffmpeg.input(input_file.as_posix()).output(output_file.as_posix(), **encoder).compile(overwrite_output=True)

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    print(f"ffmpeg started with PID {process.pid}")

    stdout, stderr = await process.communicate()

    return process.returncode

async def clean_up_files(job: Event):
    input_file = TMP_INPUT_PATH / job.data.path
    output_file = TMP_OUTPUT_PATH / job.data.path
    input_file.unlink(missing_ok=True)
    output_file.unlink(missing_ok=True)

async def node_client_loop(config: Config):
    while True:
        # try:
            ws = await get_ws_connection(config)

            # get job
            job = await get_job(ws, config)
            await download_video(config, job)
            await ws.send(Event(event="download_completed", data=CompletedDownload(node=config.client.node, id=job.data.id)).model_dump_json())

            # transcode
            code = await transcode_video(job)
            await ws.send(
                Event(
                    event="transcode_completed",
                    data=CompletedTranscode(
                        node=config.client.node,
                        id=job.data.id,
                        success=(code==0),
                    )
                ).model_dump_json())
            # upload if success
            if code == 0:
                await upload_video(config, job)
                await ws.send(
                    Event(
                        event="upload_completed",
                        data=CompletedUpload(
                            node=config.client.node,
                            id=job.data.id,
                        )
                    ).model_dump_json())

            await clean_up_files(job)


        # except Exception as e:
        #     print(e)
        #     time.sleep(1)
