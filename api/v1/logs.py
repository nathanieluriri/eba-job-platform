
from fastapi import APIRouter, HTTPException, Query, status, Path
from typing import List
from schemas.response_schema import APIResponse
from schemas.logs import (
    LogsCreate,
    LogsOut,
    LogsBase,
    LogsUpdate,
)
from services.logs_service import (
    add_logs,
    remove_logs,
    retrieve_logss,
    retrieve_logs_by_logs_id,
    update_logs_by_id,
)

router = APIRouter(prefix="/logss", tags=["Logss"])

@router.get("/", response_model=APIResponse[List[LogsOut]])
async def list_logss():
    items = await retrieve_logss()
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.get("/me", response_model=APIResponse[LogsOut])
async def get_my_logss(id: str = Query(..., description="logs ID to fetch specific item")):
    items = await retrieve_logs_by_logs_id(id=id)
    return APIResponse(status_code=200, data=items, detail="logss items fetched")


# TODO: Allow agents post logs
# TODO: Allow clients to view logs for each job 
# TODO: Allow clients to approve for each job for each client 
# TODO: Allow clients to reject logs for each job for each client 