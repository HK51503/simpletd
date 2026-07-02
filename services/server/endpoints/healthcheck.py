from fastapi import APIRouter

healthcheck_router = APIRouter(prefix="/healthcheck")

@healthcheck_router.get("")
def healthcheck():
    return {"message": "Server running!"}