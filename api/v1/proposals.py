from fastapi import APIRouter, Depends, Query
from typing import List

from schemas.response_schema import APIResponse
from schemas.proposals import JobProposalOut
from security.auth import verify_admin_token, verify_agent_token, verify_client_token, accessTokenOut
from services.proposals_service import (
    retrieve_proposals_by_job_id,
    retrieve_proposals_by_agent_id,
    retrieve_proposals_for_client,
    retrieve_proposal_for_agent,
    retrieve_proposal_for_client,
    retrieve_proposal_by_id,
)

router = APIRouter(prefix="/proposals", tags=["Proposals"])


@router.get(
    "/admin/job/{job_id}",
    description="⚠️**REQUIRES ADMIN TOKENS**",
    response_model=APIResponse[List[JobProposalOut]],
)
async def list_job_proposals_for_admin(
    job_id: str,
    start: int = Query(0, description="Start index (default: 0)"),
    stop: int = Query(100, description="Stop index (default: 100)"),
    token: dict = Depends(verify_admin_token),
):
    items = await retrieve_proposals_by_job_id(job_id=job_id, start=start, stop=stop)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.get(
    "/admin/{proposal_id}",
    description="⚠️**REQUIRES ADMIN TOKENS**",
    response_model=APIResponse[JobProposalOut],
)
async def get_proposal_for_admin(
    proposal_id: str,
    token: dict = Depends(verify_admin_token),
):
    item = await retrieve_proposal_by_id(proposal_id=proposal_id)
    return APIResponse(status_code=200, data=item, detail="Fetched successfully")


@router.get(
    "/agent/",
    description="⚠️**REQUIRES AGENT TOKENS**",
    response_model=APIResponse[List[JobProposalOut]],
)
async def list_proposals_for_agent(
    start: int = Query(0, description="Start index (default: 0)"),
    stop: int = Query(100, description="Stop index (default: 100)"),
    token: accessTokenOut = Depends(verify_agent_token),
):
    items = await retrieve_proposals_by_agent_id(agent_id=token.userId, start=start, stop=stop)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.get(
    "/agent/{proposal_id}",
    description="⚠️**REQUIRES AGENT TOKENS**",
    response_model=APIResponse[JobProposalOut],
)
async def get_proposal_for_agent(
    proposal_id: str,
    token: accessTokenOut = Depends(verify_agent_token),
):
    item = await retrieve_proposal_for_agent(proposal_id=proposal_id, agent_id=token.userId)
    return APIResponse(status_code=200, data=item, detail="Fetched successfully")


@router.get(
    "/client/",
    description="⚠️**REQUIRES CLIENT TOKENS**",
    response_model=APIResponse[List[JobProposalOut]],
)
async def list_proposals_for_client(
    start: int = Query(0, description="Start index (default: 0)"),
    stop: int = Query(100, description="Stop index (default: 100)"),
    token: accessTokenOut = Depends(verify_client_token),
):
    items = await retrieve_proposals_for_client(client_id=token.userId, start=start, stop=stop)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.get(
    "/client/{proposal_id}",
    description="⚠️**REQUIRES CLIENT TOKENS**",
    response_model=APIResponse[JobProposalOut],
)
async def get_proposal_for_client(
    proposal_id: str,
    token: accessTokenOut = Depends(verify_client_token),
):
    item = await retrieve_proposal_for_client(proposal_id=proposal_id, client_id=token.userId)
    return APIResponse(status_code=200, data=item, detail="Fetched successfully")
