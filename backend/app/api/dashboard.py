from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from ..api.dependencies import get_db
from ..services import dashboard_service

router = APIRouter()

@router.get("")
async def get_dashboard(db: Session = Depends(get_db)):
    return await run_in_threadpool(dashboard_service.get_dashboard_service, db)
