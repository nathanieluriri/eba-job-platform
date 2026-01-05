# ============================================================================
# JOB PROPOSALS REPOSITORY
# ============================================================================

from pymongo import ReturnDocument
from core.database import db
from fastapi import HTTPException, status
from typing import List, Optional
from pydantic import ValidationError

from schemas.proposals import JobProposalUpdate, JobProposalCreate, JobProposalOut


async def create_proposal(proposal_data: JobProposalCreate) -> JobProposalOut:
    proposal_dict = proposal_data.model_dump()
    result = await db.job_proposals.insert_one(proposal_dict)
    result = await db.job_proposals.find_one(filter={"_id": result.inserted_id})
    return JobProposalOut(**result)


async def get_proposal(filter_dict: dict) -> Optional[JobProposalOut]:
    try:
        result = await db.job_proposals.find_one(filter_dict)
        if result is None:
            return None
        return JobProposalOut(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching job proposal: {str(e)}",
        )


async def get_proposals(filter_dict: dict = {}, start=0, stop=100) -> List[JobProposalOut]:
    try:
        if filter_dict is None:
            filter_dict = {}

        cursor = (
            db.job_proposals.find(filter_dict)
            .skip(start)
            .limit(stop - start)
        )
        proposals_list = []
        async for doc in cursor:
            try:
                proposals_list.append(JobProposalOut(**doc))
            except ValidationError:
                continue

        return proposals_list

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching job proposals: {str(e)}",
        )


async def update_proposal(filter_dict: dict, proposal_data: JobProposalUpdate) -> JobProposalOut:
    result = await db.job_proposals.find_one_and_update(
        filter_dict,
        {"$set": proposal_data.model_dump(exclude_none=True)},
        return_document=ReturnDocument.AFTER,
    )

    return JobProposalOut(**result)


async def delete_proposal(filter_dict: dict):
    return await db.job_proposals.delete_one(filter_dict)
