# ============================================================================
# JOBS SERVICE
# ============================================================================
# This file was auto-generated on: 2025-09-27 09:11:13 WAT
# It contains  asynchrounous functions that make use of the repo functions 
# 
# ============================================================================

from bson import ObjectId
from fastapi import HTTPException
from typing import List

from repositories.jobs import (
    create_jobs,
    get_jobs,
    get_jobss,
    update_jobs,
    delete_jobs,
)
from schemas.jobs import JobsCreate, JobsUpdate, JobsOut


async def add_jobs(jobs_data: JobsCreate) -> JobsOut:
    """adds an entry of JobsCreate to the database and returns an object

    Returns:
        _type_: JobsOut
    """
    return await create_jobs(jobs_data)


async def remove_jobs(jobs_id: str):
    """deletes a field from the database and removes JobsCreateobject 

    Raises:
        HTTPException 400: Invalid jobs ID format
        HTTPException 404:  Jobs not found
    """
    if not ObjectId.is_valid(jobs_id):
        raise HTTPException(status_code=400, detail="Invalid jobs ID format")

    filter_dict = {"_id": ObjectId(jobs_id)}
    result = await delete_jobs(filter_dict)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Jobs not found")


async def retrieve_jobs_by_jobs_id(id: str) -> JobsOut:
    """Retrieves jobs object based specific Id 

    Raises:
        HTTPException 404(not found): if  Jobs not found in the db
        HTTPException 400(bad request): if  Invalid jobs ID format

    Returns:
        _type_: JobsOut
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid jobs ID format")

    filter_dict = {"_id": ObjectId(id)}
    result = await get_jobs(filter_dict)

    if not result:
        raise HTTPException(status_code=404, detail="Jobs not found")

    return result


async def retrieve_jobss(start=0,stop=100) -> List[JobsOut]:
    """Retrieves JobsOut Objects in a list

    Returns:
        _type_: JobsOut
    """
    return await get_jobss(start=start,stop=stop)


async def update_jobs_by_id(jobs_id: str, jobs_data: JobsUpdate) -> JobsOut:
    """updates an entry of jobs in the database

    Raises:
        HTTPException 404(not found): if Jobs not found or update failed
        HTTPException 400(not found): Invalid jobs ID format

    Returns:
        _type_: JobsOut
    """
    if not ObjectId.is_valid(jobs_id):
        raise HTTPException(status_code=400, detail="Invalid jobs ID format")

    filter_dict = {"_id": ObjectId(jobs_id)}
    result = await update_jobs(filter_dict, jobs_data)

    if not result:
        raise HTTPException(status_code=404, detail="Jobs not found or update failed")

    return result




async def retrieve_jobss_for_specific_client(client_id,start=0,stop=100) -> List[JobsOut]:
    """Retrieves JobsOut Objects in a list

    Returns:
        _type_: List[JobsOut]
    """
    return await get_jobss(filter_dict={"client_id":client_id},start=start,stop=stop)



async def retrieve_jobss_for_specific_agents(agent_id,start=0,stop=100) -> List[JobsOut]:
    """Retrieves JobsOut Objects in a list
    TODO: IMPLEMENT THE CONDITIONS TO RETURN ONLY JOBS A SPECIFIC AGENT QUALIFIES FOR
    Returns:
        _type_: List[JobsOut]
    """
    return await get_jobss(start=start,stop=stop)