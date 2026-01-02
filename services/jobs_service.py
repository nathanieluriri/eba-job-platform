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
from schemas.jobs import AdminJobProposal, JobsCreate, JobsUpdate, JobsOut
from services.agent_service import retrieve_agent_by_agent_id

def _agent_id_from_entry(entry) -> str | None:
    if entry is None:
        return None
    if hasattr(entry, "id"):
        return entry.id
    if isinstance(entry, dict):
        return entry.get("id") or entry.get("_id")
    return None

async def build_admin_proposal_update(
    job: JobsOut,
    proposal_data: AdminJobProposal,
    admin_user_id: str | None,
) -> JobsUpdate:
    """Create a JobsUpdate payload for an admin proposal with validated agent data."""
    if proposal_data.agent is not None:
        agent = proposal_data.agent
    else:
        agent = await retrieve_agent_by_agent_id(proposal_data.agent_id)

    selected_agents = list(job.selected_agents or [])
    for selected_agent in selected_agents:
        if _agent_id_from_entry(selected_agent) == agent.id:
            raise HTTPException(
                status_code=409,
                detail="admin has already sent agent and client this proposal before",
            )

    selected_agents.append(agent)
    return JobsUpdate(
        admin_approved=True,
        break_down=proposal_data.break_down,
        selected_agents=selected_agents,
        proposal=proposal_data.proposal,
        timeline=proposal_data.timeline,
        proposal_created_by_user_id=admin_user_id,
        proposal_created_by_role="admin",
        proposal_created_via="admin",
        proposal_agent_id=agent.id,
    )

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


async def retrieve_jobss(start=0,stop=100,filter:dict=None) -> List[JobsOut]:
    """Retrieves JobsOut Objects in a list

    Returns:
        _type_: JobsOut
    """
    if filter:
        return await get_jobss(start=start,stop=stop,filter_dict=filter)
    else: return await get_jobss(start=start,stop=stop)


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
    
    Returns:
        _type_: List[JobsOut]
    """
    
    agent =await retrieve_agent_by_agent_id(agent_id)
    
    # TODO: UNCOMMENT THE LINE BELOW TO ENABLE FILTERING BASED ON APPROVAL
    # filter_dictionary={"admin_approved":True,"primary_area_of_expertise":agent.primary_area_of_expertise}
    filter_dictionary={"admin_approved":True,"client_approved":True,"selected_agents.id": agent_id}
    
    return await get_jobss(start=start,stop=stop,filter_dict=filter_dictionary)
