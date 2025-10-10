# ============================================================================
# APPLICATIONS SERVICE
# ============================================================================
# This file was auto-generated on: 2025-10-08 23:21:51 WAT
# It contains  asynchrounous functions that make use of the repo functions 
# 
# ============================================================================

from bson import ObjectId
from fastapi import HTTPException
from typing import List

from repositories.applications import (
    create_applications,
    get_applications,
    get_applicationss,
    update_applications,
    delete_applications,
)
from schemas.applications import ApplicationsCreate, ApplicationsUpdate, ApplicationsOut


async def add_applications(applications_data: ApplicationsCreate) -> ApplicationsOut:
    """adds an entry of ApplicationsCreate to the database and returns an object

    Returns:
        _type_: ApplicationsOut
    """
    return await create_applications(applications_data)


async def remove_applications(applications_id: str):
    """deletes a field from the database and removes ApplicationsCreateobject 

    Raises:
        HTTPException 400: Invalid applications ID format
        HTTPException 404:  Applications not found
    """
    if not ObjectId.is_valid(applications_id):
        raise HTTPException(status_code=400, detail="Invalid applications ID format")

    filter_dict = {"_id": ObjectId(applications_id)}
    result = await delete_applications(filter_dict)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Applications not found")


async def retrieve_applications_by_applications_id(id: str) -> ApplicationsOut:
    """Retrieves applications object based specific Id 

    Raises:
        HTTPException 404(not found): if  Applications not found in the db
        HTTPException 400(bad request): if  Invalid applications ID format

    Returns:
        _type_: ApplicationsOut
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid applications ID format")

    filter_dict = {"_id": ObjectId(id)}
    result = await get_applications(filter_dict)

    if not result:
        raise HTTPException(status_code=404, detail="Applications not found")

    return result


async def retrieve_applicationss(agent_id:str,start=0,stop=100) -> List[ApplicationsOut]:
    """Retrieves ApplicationsOut Objects in a list

    Returns:
        _type_: ApplicationsOut
    """
    return await get_applicationss(start=start,stop=stop,filter_dict={"agent_id":agent_id})


async def update_applications_by_id(applications_id: str, applications_data: ApplicationsUpdate) -> ApplicationsOut:
    """updates an entry of applications in the database

    Raises:
        HTTPException 404(not found): if Applications not found or update failed
        HTTPException 400(not found): Invalid applications ID format

    Returns:
        _type_: ApplicationsOut
    """
    if not ObjectId.is_valid(applications_id):
        raise HTTPException(status_code=400, detail="Invalid applications ID format")

    filter_dict = {"_id": ObjectId(applications_id)}
    result = await update_applications(filter_dict, applications_data)

    if not result:
        raise HTTPException(status_code=404, detail="Applications not found or update failed")

    return result