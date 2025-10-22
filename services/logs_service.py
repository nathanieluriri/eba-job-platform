# ============================================================================
# LOGS SERVICE
# ============================================================================
# This file was auto-generated on: 2025-10-17 00:30:39 WAT
# It contains  asynchrounous functions that make use of the repo functions 
# 
# ============================================================================

from bson import ObjectId
from fastapi import HTTPException
from typing import List

from repositories.logs import (
    create_logs,
    get_logs,
    get_logss,
    update_logs,
    delete_logs,
)
from schemas.logs import LogsCreate, LogsUpdate, LogsOut


async def add_logs(logs_data: LogsCreate) -> LogsOut:
    """adds an entry of LogsCreate to the database and returns an object

    Returns:
        _type_: LogsOut
    """
    return await create_logs(logs_data)


async def remove_logs(logs_id: str):
    """deletes a field from the database and removes LogsCreateobject 

    Raises:
        HTTPException 400: Invalid logs ID format
        HTTPException 404:  Logs not found
    """
    if not ObjectId.is_valid(logs_id):
        raise HTTPException(status_code=400, detail="Invalid logs ID format")

    filter_dict = {"_id": ObjectId(logs_id)}
    result = await delete_logs(filter_dict)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Logs not found")


async def retrieve_logs_by_logs_id(id: str) -> LogsOut:
    """Retrieves logs object based specific Id 

    Raises:
        HTTPException 404(not found): if  Logs not found in the db
        HTTPException 400(bad request): if  Invalid logs ID format

    Returns:
        _type_: LogsOut
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid logs ID format")

    filter_dict = {"_id": ObjectId(id)}
    result = await get_logs(filter_dict)

    if not result:
        raise HTTPException(status_code=404, detail="Logs not found")

    return result



async def retrieve_logs_by_logs_id_and_agent_id(id: str,agent_id:str) -> LogsOut:
    """Retrieves logs object based specific Id 

    Raises:
        HTTPException 404(not found): if  Logs not found in the db
        HTTPException 400(bad request): if  Invalid logs ID format

    Returns:
        _type_: LogsOut
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid logs ID format")

    filter_dict = {"_id": ObjectId(id),"agent_id":agent_id}
    result = await get_logs(filter_dict)

    if not result:
        raise HTTPException(status_code=404, detail="Logs not found")

    return result


async def retrieve_logss(job_id,start=0,stop=100) -> List[LogsOut]:
    """Retrieves LogsOut Objects in a list

    Returns:
        _type_: LogsOut
    """
    return await get_logss(filter_dict={"job_id":job_id},start=start,stop=stop)


async def retrieve_logss_that_involve_agent_and_a_particular_job(job_id:str,agent_id:str,start=0,stop=100,) -> List[LogsOut]:
    """Retrieves LogsOut Objects in a list

    Returns:
        _type_: LogsOut
    """
    
    filter_dictionary = {"job_id":job_id,"agent_id":agent_id}
    return await get_logss(start=start,stop=stop,filter_dict=filter_dictionary)


async def update_logs_by_id(logs_id: str, logs_data: LogsUpdate) -> LogsOut:
    """updates an entry of logs in the database

    Raises:
        HTTPException 404(not found): if Logs not found or update failed
        HTTPException 400(not found): Invalid logs ID format

    Returns:
        _type_: LogsOut
    """
    if not ObjectId.is_valid(logs_id):
        raise HTTPException(status_code=400, detail="Invalid logs ID format")

    filter_dict = {"_id": ObjectId(logs_id)}
    result = await update_logs(filter_dict, logs_data)

    if not result:
        raise HTTPException(status_code=404, detail="Logs not found or update failed")

    return result