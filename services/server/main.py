import tomllib, pathlib, mimetypes, datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session, select

from config import Config
from database import create_db_and_tables, engine
from db_models import Jobs
from endpoints import videos_router, ws_router, healthcheck_router
from config import config

def is_video(file: pathlib.Path) -> bool:
    if mimetypes.guess_file_type(file)[0] and mimetypes.guess_file_type(file)[0].startswith('video'):
        return True
    return False

# todo: update sync logic
def sync_db(config: Config):
    video_dir = config.paths.video_directory
    input_folder = video_dir / "original"
    videos = [v for v in input_folder.rglob("*") if v.is_file() and is_video(v)]
    with Session(engine) as session:
        db_items = session.exec(select(Jobs).where(Jobs.deleted_at==None, Jobs.status=="pending")).all()
        videos_in_db = [input_folder / p.path for p in db_items]
        for v in videos:
            if v not in videos_in_db:
                path = v.relative_to(input_folder)
                new_job = Jobs(path=path.as_posix(), status="pending")
                session.add(new_job)
        for e in db_items:
            if input_folder / e.path not in videos:
                e.deleted_at = str(datetime.datetime.now())

        session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(videos_router)
app.include_router(ws_router)
app.include_router(healthcheck_router)


if __name__ == "__main__":
    sync_db(config)
    import uvicorn
    uvicorn.run("main:app", host=config.server.host, port=config.server.port, reload=True)
