
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends,Body
from security.auth import accessTokenOut,verify_agent_token,verify_client_token,verify_admin_token
from typing import List
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
)

router = APIRouter(prefix="/logss", tags=["Logss"])

@router.get("/agent/list/{job_id}", response_model=APIResponse[List[LogsOut]])
async def list_logss(job_id:str,token: accessTokenOut = Depends(verify_agent_token)):
    # TODO: ADD A VERIFICATION TO KNOW IF THIS USER IS ALLOWED TO VIEW THIS LOGS
    items = await retrieve_logss()
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/client/list/{job_id}", response_model=APIResponse[List[LogsOut]])
async def list_logss(job_id:str,token: accessTokenOut = Depends(verify_client_token)):
    # TODO: ADD A VERIFICATION TO KNOW IF THIS USER IS ALLOWED TO VIEW THIS LOGS
    items = await retrieve_logss()
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.get("/agent/view", response_model=APIResponse[LogsOut])
async def get_my_logss(id: str = Query(..., description="logs ID to fetch specific item"), token: accessTokenOut = Depends(verify_agent_token) ):
    # TODO: ADD A VERIFICATION TO KNOW IF THIS USER IS ALLOWED TO VIEW THIS LOGS
    items = await retrieve_logs_by_logs_id(id=id)
    return APIResponse(status_code=200, data=items, detail="logss items fetched")

@router.get("/client/view", response_model=APIResponse[LogsOut])
async def get_my_logss(id: str = Query(..., description="logs ID to fetch specific item"), token: accessTokenOut = Depends(verify_client_token) ):
    # TODO: ADD A VERIFICATION TO KNOW IF THIS USER IS ALLOWED TO VIEW THIS LOGS
    items = await retrieve_logs_by_logs_id(id=id)
    return APIResponse(status_code=200, data=items, detail="logss items fetched")

@router.patch("/approve/{log_id}", response_model=APIResponse[LogsOut])
async def client_endpoint_to_approve_logss(log_id: str, token: accessTokenOut = Depends(verify_client_token) ):
    # TODO: ADD VERIFICATION TO KNOW IF THIS CLIENT CAN APPROVE THE JOB
    try:
        update_data = LogsUpdate(client_approved=True)
        new_logs= await update_logs_by_id(logs_id=log_id,logs_data=update_data)
        return APIResponse(status_code=200,data=new_logs,details="Successfully  approved logs")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")    

@router.patch("/reject/{log_id}", response_model=APIResponse[LogsOut])
async def client_endpoint_to_reject_logss(log_id: str,log_rejection:LogReject, token: accessTokenOut = Depends(verify_client_token) ):
    # TODO: ADD VERIFICATION TO KNOW IF THIS CLIENT CAN REJECT THE JOB
    
    try:
        update_data = LogsUpdate(client_approved=False,rejection_reason=log_rejection.rejection_reason)
        new_logs= await update_logs_by_id(logs_id=log_id,logs_data=update_data)
        return APIResponse(status_code=200,data=new_logs,details="Successfully  approved logs")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}") 

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
    # TODO: ADD A VERIFICATION TO KNOW IF THIS USER IS ALLOWED TO POST LOGS FOR THIS JOB
    logs = LogsCreate(**log_data.model_dump(),agent_id=token.userId)
    item = await add_logs(applications_data=logs)
    return APIResponse(status_code=200,data=item,details="Successfully applied for the Job")


 
