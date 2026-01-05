# ============================================================================
# JOB PROPOSALS SERVICE
# ============================================================================

from bson import ObjectId
from fastapi import HTTPException
from typing import List, Optional

from repositories.proposals import (
    create_proposal,
    get_proposal,
    get_proposals,
    update_proposal,
    delete_proposal,
)
from schemas.proposals import JobProposalCreate, JobProposalUpdate, JobProposalOut
from services.jobs_service import retrieve_jobss_for_specific_client, retrieve_jobs_by_jobs_id


async def add_proposal(proposal_data: JobProposalCreate) -> JobProposalOut:
    return await create_proposal(proposal_data)


async def remove_proposal(proposal_id: str):
    if not ObjectId.is_valid(proposal_id):
        raise HTTPException(status_code=400, detail="Invalid proposal ID format")

    filter_dict = {"_id": ObjectId(proposal_id)}
    result = await delete_proposal(filter_dict)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job proposal not found")


async def retrieve_proposal_by_id(proposal_id: str) -> JobProposalOut:
    if not ObjectId.is_valid(proposal_id):
        raise HTTPException(status_code=400, detail="Invalid proposal ID format")

    filter_dict = {"_id": ObjectId(proposal_id)}
    result = await get_proposal(filter_dict)
    if not result:
        raise HTTPException(status_code=404, detail="Job proposal not found")

    return result


async def retrieve_proposals(start=0, stop=100, filter: Optional[dict] = None) -> List[JobProposalOut]:
    if filter:
        return await get_proposals(start=start, stop=stop, filter_dict=filter)
    return await get_proposals(start=start, stop=stop)


async def retrieve_proposals_by_job_id(job_id: str, start=0, stop=100) -> List[JobProposalOut]:
    return await get_proposals(filter_dict={"job_id": job_id}, start=start, stop=stop)


async def retrieve_proposals_by_agent_id(agent_id: str, start=0, stop=100) -> List[JobProposalOut]:
    return await get_proposals(filter_dict={"agent_id": agent_id}, start=start, stop=stop)


async def retrieve_proposals_for_client(client_id: str, start=0, stop=100) -> List[JobProposalOut]:
    jobs = await retrieve_jobss_for_specific_client(client_id=client_id, start=0, stop=1000)
    job_ids = [job.id for job in jobs if job.id]
    if not job_ids:
        return []
    return await get_proposals(
        filter_dict={"job_id": {"$in": job_ids}},
        start=start,
        stop=stop,
    )


async def retrieve_proposal_for_agent(proposal_id: str, agent_id: str) -> JobProposalOut:
    proposal = await retrieve_proposal_by_id(proposal_id)
    if proposal.agent_id != agent_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this proposal")
    return proposal


async def retrieve_proposal_for_client(proposal_id: str, client_id: str) -> JobProposalOut:
    proposal = await retrieve_proposal_by_id(proposal_id)
    job = await retrieve_jobs_by_jobs_id(proposal.job_id)
    if job.client_id != client_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this proposal")
    return proposal


async def update_proposal_by_id(proposal_id: str, proposal_data: JobProposalUpdate) -> JobProposalOut:
    if not ObjectId.is_valid(proposal_id):
        raise HTTPException(status_code=400, detail="Invalid proposal ID format")

    filter_dict = {"_id": ObjectId(proposal_id)}
    result = await update_proposal(filter_dict, proposal_data)
    if not result:
        raise HTTPException(status_code=404, detail="Job proposal not found or update failed")

    return result
