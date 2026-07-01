import pathlib
from fastapi import APIRouter, HTTPException, File, UploadFile, Request
from fastapi.responses import FileResponse
from sqlmodel import select
import aiofiles

from database import SessionDep
from db_models import Jobs
from config import config

videos_router = APIRouter(prefix="/videos")

@videos_router.get("/{video_id}")
async def stream_video(video_id: int, session: SessionDep):
    job = session.exec(select(Jobs).where(Jobs.deleted_at==None, Jobs.id==video_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video not found")
    video_path = pathlib.Path(config.paths.video_directory) / "original" / job.path
    return FileResponse(video_path)

@videos_router.post("/{video_id}")
async def get_video(video_id: int, session: SessionDep, request: Request):
    job = session.exec(select(Jobs).where(Jobs.deleted_at==None, Jobs.id==video_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video not found")
    else:
        video_path = pathlib.Path(config.paths.video_directory) / "output" / job.path
        video_path.parent.mkdir(exist_ok=True, parents=True)
        async with aiofiles.open(video_path, "wb") as f:
            async for chunk in request.stream():
                await f.write(chunk)
