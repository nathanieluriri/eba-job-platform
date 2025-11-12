
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends,Body
from security.auth import accessTokenOut,verify_agent_token,verify_client_token,verify_admin_token
from typing import List
from datetime import datetime,timedelta
from bson import ObjectId
from core.scheduler import scheduler
from schemas.response_schema import APIResponse
from schemas.logs import (
    LogsCreate,
    LogsOut,
    LogsBase,
    LogsUpdate,
    LogReject
)
from services.logs_service import (
    add_logs,
    remove_logs,
    retrieve_logss,
    retrieve_logs_by_logs_id,
    update_logs_by_id,
    retrieve_logss_that_involve_agent_and_a_particular_job,
    retrieve_logs_by_logs_id_and_agent_id,
)
from services.jobs_service import(
    get_jobs
)
from services.applications_service import(
    get_applications,
    
)
from schemas.applications import ProposalState
router = APIRouter(prefix="/logss", tags=["Logss"])

@router.get("/agent/list/{job_id}", response_model=APIResponse[List[LogsOut]])
async def list_logss(job_id:str,token: accessTokenOut = Depends(verify_agent_token),start:int=0,stop:int=100):
    
    items = await retrieve_logss_that_involve_agent_and_a_particular_job(job_id=job_id,agent_id=token.userId,start=start,stop=stop)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/client/list/{job_id}", response_model=APIResponse[List[LogsOut]])
async def list_logss(job_id:str,token: accessTokenOut = Depends(verify_client_token),start:int=0,stop:int=100):
    
    Job =await get_jobs(filter_dict={"client_id":token.userId,"_id":ObjectId(job_id)})
    if Job !=None:
        items = await retrieve_logss(job_id=job_id,start=start,stop=stop)
        return APIResponse(status_code=200, data=items, detail="Fetched successfully")
    else: 
        raise HTTPException(status_code=403, detail="User didn't create job so you can't view it")

@router.get("/agent/view", response_model=APIResponse[LogsOut])
async def get_my_logss(id: str = Query(..., description="logs ID to fetch specific item"), token: accessTokenOut = Depends(verify_agent_token) ):
    
    items = await retrieve_logs_by_logs_id_and_agent_id(id=id,agent_id=token.userId)
    return APIResponse(status_code=200, data=items, detail="logss items fetched")

@router.get("/client/view",response_model_exclude=None, response_model=APIResponse[LogsOut])
async def get_my_logss(job_id: str = Query(..., description="logs ID to fetch specific item"), token: accessTokenOut = Depends(verify_client_token) ):
    
    Job =await get_jobs(filter_dict={"client_id":token.userId,"_id":ObjectId(job_id)})
    if Job !=None:
        items = await retrieve_logs_by_logs_id(id=id)
        return APIResponse(status_code=200, data=items, detail="logss items fetched")
    else: 
        raise HTTPException(status_code=403, detail="User didn't create job so you can't view it")

@router.patch("/approve/{log_id}", response_model=APIResponse[LogsOut])
async def client_endpoint_to_approve_logss(log_id: str, token: accessTokenOut = Depends(verify_client_token) ):
    try:
            log = await retrieve_logs_by_logs_id(id=log_id)
    except Exception as e:
            raise HTTPException(status_code=500,detail=f"{e}")
    
    Job =await get_jobs(filter_dict={"client_id":token.userId,"_id":ObjectId(log.job_id)})
    if Job !=None:
        
        if (log.client_approved==False) and (log.rejection_reason==None):
            update_data = LogsUpdate(client_approved=True)
            
            new_logs= await update_logs_by_id(logs_id=log_id,logs_data=update_data)
            
            return APIResponse(status_code=200,data=new_logs,detail="Successfully  approved logs")
        
        elif(log.client_approved==True) and (log.rejection_reason==None): 
            raise HTTPException(status_code=409,detail="Log already approved")
        else: 
            raise HTTPException(status_code=400,detail="Bad request")
    else: 
        raise HTTPException(status_code=403, detail="User didn't create job so you can't view it")

@router.patch("/reject/{log_id}", response_model=APIResponse[LogsOut])
async def client_endpoint_to_reject_logss(log_id: str,log_rejection:LogReject, token: accessTokenOut = Depends(verify_client_token) ):
   
    try:
        log = await retrieve_logs_by_logs_id(id=log_id)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")
    Job =await get_jobs(filter_dict={"client_id":token.userId,"_id":ObjectId(log.job_id)})
    
    if Job !=None:
        
        if (log.client_approved==False) and (log.rejection_reason==None):
            
            update_data = LogsUpdate(client_approved=False,rejection_reason=log_rejection.rejection_reason)
            new_logs= await update_logs_by_id(logs_id=log_id,logs_data=update_data)
            run_time = datetime.now()+timedelta(days=7)
            scheduler.add_job(remove_logs,"date",run_date=run_time,args=[log_id],misfire_grace_time=31536000)
            
            return APIResponse(status_code=200,data=new_logs,detail="Successfully  approved logs")
        elif(log.client_approved==False) and (log.rejection_reason!=None): 
            
            raise HTTPException(status_code=409,detail="Log already rejected")
        else:
            
            raise HTTPException(status_code=400,detail="Bad request")

@router.post("/post", response_model=APIResponse[LogsOut])
async def agent_posting_new_logss(log_data: LogsBase = Body(
    ...,
    openapi_examples={
        "valid_log_entry": {
            "summary": "✅ Valid log entry",
            "description": (
                "Submit a new work log for a job. The log includes title, "
                "hours worked, optional file attachments, and a comment."
                "\n\nNote: `client_approved` is always set to `false` on creation, "
                "regardless of the input."
            ),
            "value": {
                "job_id": "job_12345",
                "log_comment": "Completed initial design and sent for review.",
                "files": ["https://design_v1.png", "https://wireframes.pdf"],
                "hours": 5,
                "log_title": "Design Phase - Round 1"
            },
        },
        "missing_fields": {
            "summary": "🚫 Missing required fields",
            "description": (
                "Example of a request missing required fields like `job_id`, `hours`, or `log_title`. "
                "This will trigger a validation error."
            ),
            "value": {
                "log_comment": "Forgot to track time for the last session.",
                "files": [],
            },
        },
        "minimal_valid_log": {
            "summary": "📝 Minimal valid log entry",
            "description": "A minimal example with only required fields filled in.",
            "value": {
                "job_id": "job_98765",
                "log_comment": "Bug fixes and testing.",
                "files": [],
                "hours": 2,
                "log_title": "QA & Testing"
            },
        },
    }
), token: accessTokenOut = Depends(verify_agent_token) ):
    
    Application =await get_applications(filter_dict={"agent_id":token.userId,"job_id":log_data.job_id})
    if Application:
        if Application.proposal_status == ProposalState.accepted:
            logs = LogsCreate(**log_data.model_dump(),agent_id=token.userId)
            item = await add_logs(logs_data=logs)
            return APIResponse(status_code=200,data=item,detail="Successfully Posted Job progress update (log) ")
        elif Application.proposal_status == ProposalState.pending_review:
            raise HTTPException(status_code=403,detail="User's application is still in the pending review state and can't post logs unless the application will be accepted")
        elif Application.proposal_status == ProposalState.rejected:
            
            raise HTTPException(status_code=403,detail="User's application has been rejected therefore user can't post logs")
    else: 
        raise HTTPException(status_code=403,detail="User didn't apply for the job so user cant post logs about it")
 
