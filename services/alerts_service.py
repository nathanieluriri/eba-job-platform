# ============================================================================
# ALERTS SERVICE
# ============================================================================
# This file was auto-generated on: 2025-09-30 13:48:50 WAT
# It contains  asynchrounous functions that make use of the repo functions 
# 
# ============================================================================

from bson import ObjectId
from fastapi import HTTPException
from typing import List

from repositories.alerts import (
    create_alerts,
    get_alerts,
    get_alertss,
    update_alerts,
    delete_alerts,
)
from schemas.alerts import AlertsCreate, AlertsUpdate, AlertsOut


async def add_alerts(alerts_data: AlertsCreate) -> AlertsOut:
    """adds an entry of AlertsCreate to the database and returns an object

    Returns:
        _type_: AlertsOut
    """
    return await create_alerts(alerts_data)


async def remove_alerts(alerts_id: str):
    """deletes a field from the database and removes AlertsCreateobject 

    Raises:
        HTTPException 400: Invalid alerts ID format
        HTTPException 404:  Alerts not found
    """
    if not ObjectId.is_valid(alerts_id):
        raise HTTPException(status_code=400, detail="Invalid alerts ID format")

    filter_dict = {"_id": ObjectId(alerts_id)}
    result = await delete_alerts(filter_dict)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alerts not found")


async def retrieve_alerts_by_alerts_id(id: str) -> AlertsOut:
    """Retrieves alerts object based specific Id 

    Raises:
        HTTPException 404(not found): if  Alerts not found in the db
        HTTPException 400(bad request): if  Invalid alerts ID format

    Returns:
        _type_: AlertsOut
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid alerts ID format")

    filter_dict = {"_id": ObjectId(id)}
    result = await get_alerts(filter_dict)

    if not result:
        raise HTTPException(status_code=404, detail="Alerts not found")

    return result


async def retrieve_alertss(start=0,stop=100) -> List[AlertsOut]:
    """Retrieves AlertsOut Objects in a list

    Returns:
        _type_: AlertsOut
    """
    return await get_alertss(start=start,stop=stop)


async def update_alerts_by_id(alerts_id: str, alerts_data: AlertsUpdate) -> AlertsOut:
    """updates an entry of alerts in the database

    Raises:
        HTTPException 404(not found): if Alerts not found or update failed
        HTTPException 400(not found): Invalid alerts ID format

    Returns:
        _type_: AlertsOut
    """
    if not ObjectId.is_valid(alerts_id):
        raise HTTPException(status_code=400, detail="Invalid alerts ID format")

    filter_dict = {"_id": ObjectId(alerts_id)}
    result = await update_alerts(filter_dict, alerts_data)

    if not result:
        raise HTTPException(status_code=404, detail="Alerts not found or update failed")

    return result