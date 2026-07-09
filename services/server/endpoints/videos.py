import pathlib
from fastapi import APIRouter, HTTPException, File, UploadFile, Request
from fastapi.responses import FileResponse
from sqlmodel import select
import aiofiles

from database import SessionDep
from db.models import Job
from config import config

videos_router = APIRouter(prefix="/videos")

@videos_router.get("/{video_id}")
async def stream_video(video_id: int, session: SessionDep):
    job = session.exec(select(Jobs).where(Job.deleted_at==None, Job.id==video_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video not found")
    # only works for local, add stuff for smb
    video_path = job.library.storage.data.path / job.library.input_path / job.path
    return FileResponse(video_path)

@videos_router.post("/{video_id}")
async def get_video(video_id: int, session: SessionDep, request: Request):
    job = session.exec(select(Job).where(Job.deleted_at==None, Job.id==video_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video not found")
    else:
        video_path = job.library.storage.data.path / job.library.output_path / job.path
        video_path.parent.mkdir(exist_ok=True, parents=True)
        async with aiofiles.open(video_path, "wb") as f:
            async for chunk in request.stream():
                await f.write(chunk)
