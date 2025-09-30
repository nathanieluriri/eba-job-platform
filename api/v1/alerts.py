
from fastapi import APIRouter, HTTPException, Query, status, Path
from typing import List
from schemas.response_schema import APIResponse
from schemas.alerts import (
    AlertsCreate,
    AlertsOut,
    AlertsBase,
    AlertsUpdate,
)
from services.alerts_service import (
    add_alerts,
    remove_alerts,
    retrieve_alertss,
    retrieve_alerts_by_alerts_id,
    update_alerts,
)

router = APIRouter(prefix="/alertss", tags=["Alertss"])

@router.get("/", response_model=APIResponse[List[AlertsOut]])
async def list_alertss():
    items = await retrieve_alertss()
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/me", response_model=APIResponse[AlertsOut])
async def get_my_alertss(id: str = Query(..., description="alerts ID to fetch specific item")):
    items = await retrieve_alerts_by_alerts_id(id=id)
    return APIResponse(status_code=200, data=items, detail="alertss items fetched")
