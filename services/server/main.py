import pathlib, mimetypes, datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session, select, col

from database import create_db_and_tables, engine
from db.models import Job, Library, StorageConfig
from endpoints import videos_router, ws_router, healthcheck_router
from config import config

def is_video(file: pathlib.Path) -> bool:
    if mimetypes.guess_file_type(file)[0] and mimetypes.guess_file_type(file)[0].startswith('video'):
        return True
    return False

# todo: update sync logic
def sync_db():
    with Session(engine) as session:
        libraries = session.exec(select(Library).where(Library.deleted_at==None)).all()
        for l in libraries:
            if l.sync:
                storage = session.exec(select(StorageConfig).where(StorageConfig.id==l.storage_id, StorageConfig.deleted_at==None)).first()
                pending_videos = session.exec(select(Job).where(Job.deleted_at == None, Job.library_id == l.id, Job.status == "pending")).all()
                match storage.mode:
                    case "local":
                        input_folder = storage.config.path / l.input_path
                        print(input_folder.as_posix())
                        original_videos_paths = [v for v in input_folder.rglob("*") if v.is_file() and is_video(v)]
                        pending_videos_paths = [input_folder/v.path for v in pending_videos]
                        for v in original_videos_paths:
                            if v not in pending_videos_paths:
                                path = v.relative_to(input_folder)
                                new_job = Job(library_id=l.id, path=path.as_posix(), status="pending")
                                session.add(new_job)
                        for j in pending_videos:
                            if input_folder / j.path not in original_videos_paths:
                                j.deleted_at = str(datetime.datetime.now())
                    case _:
                        ...
        session.commit()



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    sync_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(videos_router)
app.include_router(ws_router)
app.include_router(healthcheck_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.server.host, port=config.server.port, reload=True)
