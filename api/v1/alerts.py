
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends,Body
from typing import List,Annotated
from security.auth import verify_token,verify_admin_token
from celery_worker import celery_app
from schemas.response_schema import APIResponse
from schemas.alerts import (
    AlertsCreate,
    AlertsOut,
    AlertsBase,
    AlertsUpdate,
    alert_examples,
    AlertActions,
    UserTypes,
    ListOfAlertsOut
    
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
    response_model=APIResponse[ListOfAlertsOut],
    summary="Get agent alerts",
    description="Fetches all alerts that belong to an authenticated agent."
)
async def list_agents_alertss(token: accessTokenOut = Depends(verify_token)):
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
    items = await retrieve_alertss(user_type=UserTypes.agent,user_id=token.userId)
    
    unread_items = [item for item in items if item.unread]
    List_of_items =ListOfAlertsOut(alerts=items,total_number_of_unread=len(unread_items))
    return APIResponse(status_code=200, data=List_of_items, detail="Fetched successfully")


@router.get(
    "/client",
    response_model=APIResponse[ListOfAlertsOut],
    summary="Get client alerts",
    description="Fetches all alerts that belong to an authenticated client."
)
async def list_clients_alertss(token: accessTokenOut = Depends(verify_token)):
    """
    Retrieve all client for an authenticated agent.

    This endpoint fetches a list of alerts that belong to the currently
    authenticated user. The user is authenticated via their access token.

    Args:
        token (accessTokenOut): The decoded access token returned after 
            validating the user's token using `verify_token`.

    Returns:
        APIResponse[List[AlertsOut]]: A structured API response containing
        a list of user-specific alerts.
    """
    items = await retrieve_alertss(user_type=UserTypes.client,user_id=token.userId)
    
    unread_items = [item for item in items if item.unread]
    List_of_items =ListOfAlertsOut(alerts=items,total_number_of_unread=len(unread_items))
    return APIResponse(status_code=200, data=List_of_items, detail="Fetched successfully")




@router.get(
    "/admin",
    dependencies=[Depends(verify_admin_token)],
    response_model=APIResponse[ListOfAlertsOut],
    summary="Get all alerts (Admin)",
    description="Fetches all admin alerts in the system. Only accessible by admins."
)
async def list_admin_alertss(token=Depends(verify_admin_token)):
    """
    Retrieve all alerts (admin only).

    This endpoint fetches all alerts across all users. 
    It requires admin authentication via the `verify_admin_token` dependency.

    Returns:
        APIResponse[List[AlertsOut]]: A structured API response containing
        a list of all alerts in the system (admin scope).
    """

    items = await retrieve_alertss(user_type=UserTypes.admin,user_id=token.get("userId"))
    
    unread_items = [item for item in items if item.unread]
    List_of_items =ListOfAlertsOut(alerts=items,total_number_of_unread=len(unread_items))
    return APIResponse(status_code=200, data=List_of_items, detail="Fetched successfully")


@router.get("/admin/read", response_model=APIResponse[ListOfAlertsOut])
async def read_admin_alerts(token: accessTokenOut = Depends(verify_admin_token)):
    """
    Returns List of Unread admin alerts while spinning up a task to mark read for all unread alerts 

    Args:
        token (accessTokenOut, optional): _description_. Defaults to Depends(verify_admin_token).

    Returns:
        _type_: ListOfAlertsOut
    """
    items = await retrieve_alertss(user_type=UserTypes.admin,user_id=token.get("userId"))
    unread_items = [item for item in items if item.unread]
    List_of_items =ListOfAlertsOut(alerts=unread_items,total_number_of_unread=len(unread_items))
    result = celery_app.send_task("celery_worker.update_unread_alerts", args=[[item.model_dump() for item in unread_items]])
    return APIResponse(status_code=200, data=List_of_items, detail="Fetched successfully")


@router.get("/client/read", response_model=APIResponse[ListOfAlertsOut])
async def read_clients_alertss(token: accessTokenOut = Depends(verify_token)):
    """
    Returns List of Unread client alerts while spinning up a task to mark read for all unread alerts 

    Args:
        token (accessTokenOut, optional): _description_. Defaults to Depends(verify_admin_token).

    Returns:
        _type_: ListOfAlertsOut
    """
    items = await retrieve_alertss(user_type=UserTypes.client,user_id=token.userId)
    unread_items = [item for item in items if item.unread]
    List_of_items =ListOfAlertsOut(alerts=unread_items,total_number_of_unread=len(unread_items))
    result = celery_app.send_task("celery_worker.update_unread_alerts", args=[[item.model_dump() for item in unread_items]])
    return APIResponse(status_code=200, data=List_of_items, detail="Fetched successfully")

@router.get("/agent/read", response_model=APIResponse[ListOfAlertsOut])
async def read_agents_alertss(token: accessTokenOut = Depends(verify_token)):
    items = await retrieve_alertss(user_type=UserTypes.agent,user_id=token.userId)
    unread_items = [item for item in items if item.unread]
    List_of_items =ListOfAlertsOut(alerts=unread_items,total_number_of_unread=len(unread_items))
    result = celery_app.send_task("celery_worker.update_unread_alerts", args=[[item.model_dump() for item in unread_items]])
    return APIResponse(status_code=200, data=List_of_items, detail="Fetched successfully")



@router.post(
    "/test-alert-creation",
    
    response_model_exclude_none=True,
    tags=["Alerts"]
)
async def create_test_alert(
    alert_data: Annotated[
        AlertsBase,
        Body(
            openapi_examples=alert_examples
        ),
    ]
):
    """
    Test endpoint for creating a new alert.
    
    This endpoint accepts an alert payload and returns it,
    showcasing different examples in the API documentation.
    """
    # In a real app, you would save this alert_data to the database.
    # For this test, we just return the data we received.
    alert =AlertsCreate(**alert_data.model_dump())
    new_alert = await add_alerts(alerts_data=alert)
    return APIResponse(
        status_code=200,
        data=new_alert,
        detail=f"Test alert created successfully for user {alert_data.user_id}"
    )
