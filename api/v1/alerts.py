
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends
from typing import List,Annotated
from security.auth import verify_token,verify_admin_token
from schemas.response_schema import APIResponse
from schemas.alerts import (
    AlertsCreate,
    AlertsOut,
    AlertsBase,
    AlertsUpdate,
    AlertActions,
    
)
from schemas.tokens_schema import (
    accessTokenOut,
    accessTokenBase
)
from services.alerts_service import (
    add_alerts,
    remove_alerts,
    retrieve_alertss,
    retrieve_alerts_by_alerts_id,
    update_alerts,
)

router = APIRouter(prefix="/alertss", tags=["Alertss"])

@router.get(
    "/agent",
    response_model=APIResponse[List[AlertsOut]],
    summary="Get agent alerts",
    description="Fetches all alerts that belong to an authenticated agent."
)
async def list_user_alertss(token: accessTokenOut = Depends(verify_token)):
    """
    Retrieve all alerts for an agent.

    This endpoint fetches a list of alerts that belong to the currently
    authenticated user. The user is authenticated via their access token.

    Args:
        token (accessTokenOut): The decoded access token returned after 
            validating the user's token using `verify_token`.

    Returns:
        APIResponse[List[AlertsOut]]: A structured API response containing
        a list of user-specific alerts.
    """
    items = await retrieve_alertss()
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.get(
    "/client",
    response_model=APIResponse[List[AlertsOut]],
    summary="Get client alerts",
    description="Fetches all alerts that belong to an authenticated client."
)
async def list_user_alertss(token: accessTokenOut = Depends(verify_token)):
    """
    Retrieve all alerts for an authenticated agent.

    This endpoint fetches a list of alerts that belong to the currently
    authenticated user. The user is authenticated via their access token.

    Args:
        token (accessTokenOut): The decoded access token returned after 
            validating the user's token using `verify_token`.

    Returns:
        APIResponse[List[AlertsOut]]: A structured API response containing
        a list of user-specific alerts.
    """
    items = await retrieve_alertss()
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")




@router.get(
    "/admin",
    dependencies=[Depends(verify_admin_token)],
    response_model=APIResponse[List[AlertsOut]],
    summary="Get all alerts (Admin)",
    description="Fetches all admin alerts in the system. Only accessible by admins."
)
async def list_admin_alertss():
    """
    Retrieve all alerts (admin only).

    This endpoint fetches all alerts across all users. 
    It requires admin authentication via the `verify_admin_token` dependency.

    Returns:
        APIResponse[List[AlertsOut]]: A structured API response containing
        a list of all alerts in the system (admin scope).
    """
    items = await retrieve_alertss()
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.get("/admin/me", response_model=APIResponse[AlertsOut])
async def get_my_alertss(id: str = Query(..., description="alerts ID to fetch specific alert action for admin"),token: accessTokenOut = Depends(verify_token)):
    items = await retrieve_alerts_by_alerts_id(id=id)
    return APIResponse(status_code=200, data=items, detail="alertss items fetched")


@router.get("/client/me", response_model=APIResponse[AlertsOut])
async def get_my_alertss(id: str = Query(..., description="alerts ID to fetch specific alert action for admin")):
    items = await retrieve_alerts_by_alerts_id(id=id)
    return APIResponse(status_code=200, data=items, detail="alertss items fetched")

@router.get("/agent/me", response_model=APIResponse[AlertsOut])
async def get_my_alertss(id: str = Query(..., description="alerts ID to fetch specific alert action for admin")):
    items = await retrieve_alerts_by_alerts_id(id=id)
    return APIResponse(status_code=200, data=items, detail="alertss items fetched")