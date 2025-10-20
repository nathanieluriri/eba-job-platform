from fastapi import APIRouter, HTTPException, Query, status, Path,Depends,Body
from typing import List
from bson import ObjectId
from core.scheduler import scheduler
from datetime import datetime,timedelta
from schemas.response_schema import APIResponse
from security.auth import verify_agent_token,accessTokenOut,verify_admin_token,verify_client_token
from schemas.applications import (
    ApplicationsCreate,
    ApplicationsOut,
    ApplicationsBase,
    ApplicationsUpdate,
    ApplicationAccept,
    ApplicationReject,
    ProposalState
)
from schemas.jobs import (
    JobsOut,
    JobsUpdate,
)
from services.agent_service import (
    retrieve_agent_by_agent_id
)
from services.applications_service import (
    add_applications,
    remove_applications,
    retrieve_applicationss,
    retrieve_applications_by_applications_id,
    retrieve_applications_by_applications_id_and_agent_id,
    update_applications_by_id,
)
from services.jobs_service import (

    get_jobs,
    retrieve_jobs_by_jobs_id,
    update_jobs_by_id,
)

router = APIRouter(prefix="/applicationss", tags=["Applicationss"])

@router.get("/agent/list", response_model=APIResponse[List[ApplicationsOut]])
async def list_all_job_applications_agent_has_ever_applied_for(start:int= Query(..., description="where to start the query from usually 0 used to return a list of the item"),stop:int= Query(..., description="where to end the query at usually ends withs 100 used to return a list of the item"),token: accessTokenOut = Depends(verify_agent_token),):
    items = await retrieve_applicationss(start=start,stop=stop,agent_id=token.userId)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")



@router.get("/client/list", response_model=APIResponse[List[ApplicationsOut]])
async def list_applications_clients_have_for_a_particular_job( job_id: str = Query(..., description="Job ID to fetch specific application item"),start:int= Query(..., description="where to start the query from usually 0 used to return a list of the item"),stop:int= Query(..., description="where to end the query at usually ends withs 100 used to return a list of the item"),token: accessTokenOut = Depends(verify_client_token),):
    applications=[]
    jobs  =await get_jobs(filter_dict={"client_id":token.userId,"_id":ObjectId(job_id)})
    if jobs:
        print(jobs)    
        items = await retrieve_applicationss(start=start,stop=stop,job_id=job_id)
        for application in items:
            agent_details = await retrieve_agent_by_agent_id(id=application.agent_id)
            application.agent_details=agent_details
            applications.append(application) 
        return APIResponse(status_code=200, data=applications, detail="Fetched successfully")
    return APIResponse(status_code=403,data="User Doesn't have any job with this job id",detail="Unauthorized Access")


@router.get("/admin/me", response_model=APIResponse[ApplicationsOut],dependencies=[Depends(verify_admin_token)])
async def get_applications_object_using_admin_tokens(id: str = Query(..., description="applications ID to fetch specific item")):
    items = await retrieve_applications_by_applications_id(id=id)
    return APIResponse(status_code=200, data=items, detail="applicationss items fetched")


@router.get("/admin/list", response_model=APIResponse[List[ApplicationsOut]],dependencies=[Depends(verify_admin_token)])
async def list_applications_for_a_particular_job( job_id: str = Query(..., description="Job ID to fetch specific application item"),start:int= Query(...,  description="where to start the query from usually 0 used to return a list of the item"),stop:int= Query(..., description="where to end the query at usually ends withs 100 used to return a list of the item")):
    items = await retrieve_applicationss(start=start,stop=stop)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")



@router.get("/client/me", response_model=APIResponse[ApplicationsOut])
async def get_application_object_using_client_token( token:accessTokenOut=Depends(verify_client_token),id: str = Query(..., description="applications ID to fetch specific item"),job_id: str = Query(..., description="Job ID to fetch specific application item")):
    jobs  =await get_jobs(filter_dict={"client_id":token.userId,"_id":ObjectId(job_id)})
    if jobs:
        print(jobs)    
        application = await retrieve_applications_by_applications_id(id=id)
        agent_details = await retrieve_agent_by_agent_id(id=application.agent_id)
        application.agent_details=agent_details
        return APIResponse(status_code=200, data=application, detail="applicationss items fetched")
    return APIResponse(status_code=403,data="User Doesn't have any job with this job id",detail="Unauthorized Access")

@router.patch("/client/select-agent/{job_id}", response_model=APIResponse[ApplicationsOut],dependencies=[Depends(verify_client_token)])
async def approve_agent_job_application(acceptance_data:ApplicationAccept,job_id:str,token:accessTokenOut=Depends(verify_client_token)):
    jobs  =await get_jobs(filter_dict={"client_id":token.userId,"_id":ObjectId(job_id)})
    if jobs:
        print(jobs)  
        update_data = ApplicationsUpdate(proposal_status=ProposalState.accepted) 
        item = await update_applications_by_id(applications_id=acceptance_data.id,applications_data=update_data)
        return APIResponse(status_code=200, data=item, detail="applications updated successfully")
    return APIResponse(status_code=403,data="User Doesn't have any job with this job id",detail="Unauthorized Access")

@router.patch("/client/reject-agent/{job_id}", response_model=APIResponse[ApplicationsOut],dependencies=[Depends(verify_client_token)])
async def reject_agent_job_application(rejection_data:ApplicationReject,job_id:str,token:accessTokenOut=Depends(verify_client_token)):
    jobs  =await get_jobs(filter_dict={"client_id":token.userId,"_id":ObjectId(job_id)})
    
    if jobs:
        print(jobs)  
        update_data = ApplicationsUpdate(proposal_status=ProposalState.rejected,rejection_reason=rejection_data.rejection_reason) 
        item = await update_applications_by_id(applications_id=rejection_data.application_id,applications_data=update_data)
        
        run_time = datetime.now()+timedelta(days=30)
        scheduler.add_job(remove_applications,"date",run_date=run_time,args=[rejection_data.application_id],misfire_grace_time=31536000)
        
        return APIResponse(status_code=200, data=item, detail="applications updated successfully")
    return APIResponse(status_code=403,data="User Doesn't have any job with this job id",detail="Unauthorized Access")




@router.get("/agent/me", response_model=APIResponse[ApplicationsOut])
async def get_my_applicationss(id: str = Query(..., description="applications ID to fetch specific item"),token:accessTokenOut=Depends(verify_agent_token)):
    items = await retrieve_applications_by_applications_id_and_agent_id(id=id,agent_id=token.userId)
    if items:
        return APIResponse(status_code=200, data=items, detail="applicationss items fetched")
    else: raise HTTPException(status_code=403, detail="Unauthorized request")


@router.post("/apply")
async def agent_applying_for_job(application_data: ApplicationsBase = Body(
    ...,
    openapi_examples={
        "valid_application": {
            "summary": "✅ Submit a valid application",
            "description": (
                "A freelancer applies to a job with a valid proposal. "
                "The `job_id` must be the identifier of an existing job posting, "
                "and the `proposal` should clearly explain the candidate’s approach or value."
            ),
            "value": {
                "job_id": "job_abc123",
                "proposal": (
                    "Hi there, I have 5+ years of experience with similar projects. "
                    "I can start immediately and deliver within your timeline. "
                    "Looking forward to working with you!"
                ),
            },
        },
        "short_proposal": {
            "summary": "⚠️ Too short proposal",
            "description": (
                "A minimal or low-effort proposal might be rejected depending on validation rules "
                "or platform moderation policies."
            ),
            "value": {
                "job_id": "job_xyz789",
                "proposal": "I'm interested."
            },
        },
        "missing_job_id": {
            "summary": "🚫 Missing required field",
            "description": (
                "This example is missing the `job_id` field, which is required. "
                "The API will return a validation error."
            ),
            "value": {
                "proposal": "I have experience with similar tasks."
            },
        },
    }
), token: accessTokenOut = Depends(verify_agent_token),):
    # TODO: ADD VERIFICATION HERE ONLY AN AGENT THAT HAS THE ACCURATE SKILLS CAN APPLY TO A JOB WITH THEIR SKILLS
    application = ApplicationsCreate(**application_data.model_dump(),agent_id=token.userId,proposal_status=ProposalState.pending_review)
    filter_dictionary = {"_id":ObjectId(application.job_id)}
    current_job =await get_jobs(filter_dict=filter_dictionary)
    
    if (current_job.admin_approved==True) and (current_job.isCompleted==False):
        item = await add_applications(applications_data=application)
        return APIResponse(status_code=200,data=item,detail="Successfully applied for the Job")
    else: 
        raise HTTPException(status_code=403,detail="Job is not accepting applications") 