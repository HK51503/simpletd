import datetime
from fastapi import APIRouter, WebSocket

from shared_protocol import Event, FoundJob

from sqlmodel import Session, select

from database import engine
from db_models import Jobs

ws_router = APIRouter(prefix="/ws")

@ws_router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        event = Event(**await websocket.receive_json())
        with Session(engine) as session:
            match event.event:
                case "get_job":
                    job = session.exec(select(Jobs).where(Jobs.deleted_at==None, Jobs.status=="pending")).first()
                    if job:
                        job.node = event.data.node
                        job.status = "downloading"
                        session.add(job)
                        session.commit()
                        encoder = {"vcodec": "libsvtav1", "preset": 4, "crf": 26}
                        await websocket.send_json(Event(event="job_found", data=FoundJob(**{"id": job.id, "path": job.path, "encoder": encoder})).model_dump())
                    else:
                        await websocket.send_json(Event(event="job_not_found", data=None).model_dump())

                case "download_completed":
                    job = session.exec(select(Jobs).where(Jobs.deleted_at==None, Jobs.id==event.data.id)).first()
                    if job.status == "downloading":
                        job.status = "transcoding"
                        job.start_time = str(datetime.datetime.now())
                        session.add(job)
                        session.commit()

                case "transcode_completed":
                    job = session.exec(select(Jobs).where(Jobs.deleted_at == None, Jobs.id == event.data.id)).first()
                    if job.status == "transcoding":
                        if event.data.success:
                            job.status = "uploading"
                        else:
                            job.status = "failed"
                        job.end_time = str(datetime.datetime.now())
                        session.add(job)
                        session.commit()

                case "upload_completed":
                    job = session.exec(select(Jobs).where(Jobs.deleted_at == None, Jobs.id == event.data.id)).first()
                    if job.status == "uploading":
                        job.status = "completed"
                        job.end_time = str(datetime.datetime.now())
                        session.add(job)
                        session.commit()
