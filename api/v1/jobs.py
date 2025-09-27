
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends
from typing import List
from schemas.response_schema import APIResponse
from security.auth import verify_client_token,accessTokenOut,verify_agent_token,verify_admin_token
from schemas.jobs import (
    JobsCreate,
    JobsOut,
    JobsBase,
    JobsUpdate,
)
from services.jobs_service import (
    add_jobs,
    remove_jobs,
    retrieve_jobss,
    retrieve_jobs_by_jobs_id,
    update_jobs,
    retrieve_jobss_for_specific_client,
    retrieve_jobss_for_specific_agents
)

router = APIRouter(prefix="/jobss", tags=["Jobss"])

@router.get("/agent/available/{start}/{stop}",  description="⚠️ **REQUIRES AGENT TOKENS**", response_model=APIResponse[List[JobsOut]])
async def list_jobss_agent_qualifies_for(start:int=0,stop:int=100,token:accessTokenOut = Depends(verify_agent_token)):
    items = await retrieve_jobss_for_specific_agents(start=start,stop=stop)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/client/created/{start}/{stop}",description="⚠️**REQUIRES CLIENT TOKENS**", response_model=APIResponse[List[JobsOut]])
async def list_jobss_client_made(start:int=0,stop:int=100,token:accessTokenOut = Depends(verify_client_token)):
    items = await retrieve_jobss_for_specific_client(client_id=token.userId,start=start,stop=stop)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.get("/admin/{start}/{stop}",description="⚠️**REQUIRES ADMIN TOKENS**", response_model=APIResponse[List[JobsOut]])
async def list_jobss(start:int=0,stop:int=100,token:accessTokenOut = Depends(verify_admin_token)):
    items = await retrieve_jobss(start=start,stop=stop)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/me",description="⚠️**REQUIRES ADMIN TOKENS**", response_model=APIResponse[JobsOut])
async def get_my_jobss(id: str = Query(..., description="jobs ID to fetch specific item"),tokentoken:accessTokenOut = Depends(verify_admin_token)):
    items = await retrieve_jobs_by_jobs_id(id=id)
    return APIResponse(status_code=200, data=items, detail="jobss items fetched")


@router.post("/", description="⚠️**REQUIRES CLIENT TOKENS**",response_model=APIResponse[JobsOut])
async def get_my_jobss(data:JobsBase,token:accessTokenOut = Depends(verify_client_token)):
    job_data = JobsCreate(**data.model_dump(),client_id=token.userId)
    items = await add_jobs(jobs_data=job_data)
    return APIResponse(status_code=200, data=items, detail="jobss items fetched")
