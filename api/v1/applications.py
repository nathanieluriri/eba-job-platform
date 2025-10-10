
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends
from typing import List
from schemas.response_schema import APIResponse
from security.auth import verify_agent_token,accessTokenOut,verify_admin_token,verify_client_token
from schemas.applications import (
    ApplicationsCreate,
    ApplicationsOut,
    ApplicationsBase,
    ApplicationsUpdate,
    ProposalState
)
from services.applications_service import (
    add_applications,
    remove_applications,
    retrieve_applicationss,
    retrieve_applications_by_applications_id,
    update_applications_by_id,
)

router = APIRouter(prefix="/applicationss", tags=["Applicationss"])

@router.get("/agent/{start}/{stop}", response_model=APIResponse[List[ApplicationsOut]])
async def list_all_job_applications_agent_has_ever_applied_for( start:int,stop:int,token: accessTokenOut = Depends(verify_agent_token),):
    items = await retrieve_applicationss(start=start,stop=stop,agent_id=token.userId)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")



@router.get("/client/{start}/{stop}/{job_id}", response_model=APIResponse[List[ApplicationsOut]])
async def list_applications_clients_have_for_a_particular_job( start:int,stop:int,token: accessTokenOut = Depends(verify_client_token),):
    # TODO: write function to check if the client created the job he wants to search
    
    items = await retrieve_applicationss(start=start,stop=stop,agent_id=token.userId)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.get("/admin/me", response_model=APIResponse[ApplicationsOut],dependencies=[Depends(verify_admin_token)])
async def get_applications_object_using_admin_tokens(id: str = Query(..., description="applications ID to fetch specific item")):
    items = await retrieve_applications_by_applications_id(id=id)
    return APIResponse(status_code=200, data=items, detail="applicationss items fetched")

# TODO: Implement a list application for admins just incase copy the same stuff from client but remove validation functions


@router.get("/client/me", response_model=APIResponse[ApplicationsOut],dependencies=[Depends(verify_client_token)])
async def get_application_object_using_client_token(id: str = Query(..., description="applications ID to fetch specific item")):
    # TODO: write function to check if the client created the job he wants to search
    
    items = await retrieve_applications_by_applications_id(id=id)
    return APIResponse(status_code=200, data=items, detail="applicationss items fetched")

@router.patch("/client/select-agent", response_model=APIResponse[ApplicationsOut],dependencies=[Depends(verify_client_token)])
async def approve_or_reject_agent_job_application():
    # TODO: Implement functions for selecting agent currently the database model I've got in my head isn't really making sense maybe something else should be thought of
    pass


@router.get("/agent/me", response_model=APIResponse[ApplicationsOut])
async def get_my_applicationss(id: str = Query(..., description="applications ID to fetch specific item")):
    items = await retrieve_applications_by_applications_id(id=id)
    return APIResponse(status_code=200, data=items, detail="applicationss items fetched")


@router.post("/")
async def agent_applying_for_job(application_data:ApplicationsBase, token: accessTokenOut = Depends(verify_agent_token),):
    application = ApplicationsCreate(**application_data.model_dump(),agent_id=token.userId,proposal_status=ProposalState.pending_review)
    item = await add_applications(applications_data=application)
    return APIResponse(status_code=200,data=item,details="Successfully applied for the Job")