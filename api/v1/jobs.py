
import time
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends,Body
from typing import Any, List, Union
from datetime import datetime, timedelta
from core.scheduler import scheduler
from schemas.agent import AgentOut
from schemas.alerts import AlertsBase, AlertsCreate
from schemas.imports import AlertType, PriorityStatus, UserTypes
from schemas.response_schema import APIResponse
from security.auth import verify_client_token,accessTokenOut,verify_agent_token,verify_admin_token
from celery_worker import celery_app
from schemas.jobs import (
    JobMeeting,
    JobsCreate,
    JobsOut,
    JobsBase,
    PriceBreakDown,
    JobStatus,
    JobsUpdate,
    JobStatus,
    
)
from bson import ObjectId
from services.agent_service import retrieve_agents
from services.alerts_service import add_alerts
from services.jobs_service import (
    add_jobs,
    remove_jobs,
    retrieve_jobss,
    retrieve_jobs_by_jobs_id,
    update_jobs_by_id,
    retrieve_jobss_for_specific_client,
    retrieve_jobss_for_specific_agents,
    get_jobs,
)

router = APIRouter(prefix="/jobss", tags=["Jobss"])
# TODO: NEW FLOW FOR THE JOB POSTING IS WHEN CLIENTS POST JOBS ADMIN MAKE EDITS PLUS RECOMMEND AGENTS FOR CLIENTS TO JUDGE

@router.get("/agent/",  description="⚠️ **REQUIRES AGENT TOKENS**", response_model=APIResponse[List[JobsOut]])
async def list_jobs_agent_has_been_selected_for(start:int= Query(...,  description="where to start the query from usually 0 used to return a list of the item"),stop:int= Query(...,  description="where to end the query at usually ends withs 100 used to return a list of the item"),token:accessTokenOut = Depends(verify_agent_token)):
    items = await retrieve_jobss_for_specific_agents(agent_id=token.userId,start=start,stop=stop)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/client/created/",description="⚠️**REQUIRES CLIENT TOKENS**", response_model=APIResponse[List[JobsOut]])
async def list_jobss_client_made(start:int= Query(...,  description="where to start the query from usually 0 used to return a list of the item"),stop:int= Query(...,  description="where to end the query at usually ends withs 100 used to return a list of the item"),token:accessTokenOut = Depends(verify_client_token)):
    items = await retrieve_jobss_for_specific_client(client_id=token.userId,start=start,stop=stop)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")



@router.get(
    "/admin/",
    description="⚠️**REQUIRES ADMIN TOKENS**",
    response_model=APIResponse[List[JobsOut]]
)
async def list_jobss(
    start: int = Query(
        
        description="Start index (default: 0)",
        examples={
            "example_start": {
                "summary": "Start at the first job",
                "description": "This sets the starting index of the jobs list to fetch. ⚠️ **REQUIRES ADMIN TOKENS**",
                "value": 0
            }
        }
    ),
    stop: int = Query(
        description="Stop index (default: 100)",
        examples={
            "example_stop": {
                "summary": "Fetch up to 100 jobs",
                "description": "This sets the stopping index of the jobs list to fetch.",
                "value": 100
            }
        }
    ),
    token: accessTokenOut = Depends(verify_admin_token),
):
    items = await retrieve_jobss(start=start, stop=stop)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.get(
    "/me",
    description="⚠️**REQUIRES ADMIN TOKENS**",
    response_model=APIResponse[JobsOut]
)
async def get_my_jobss(
    id: str = Query(
        ...,
        description="Job ID to fetch a specific job item.",
        examples={
            "job_id_example": {
                "summary": "Fetch a specific Job",
                "description": (
                    "Provide the unique job ID to fetch details about a specific job. "
                    "This endpoint requires **Admin authentication tokens**."
                    "⚠️ **REQUIRES CLIENT TOKENS**"
                ),
                "value": "job_64a7f91e92d8b3aef1234567"
            }
        }
    ),
    tokentoken: accessTokenOut = Depends(verify_admin_token),
):
    items = await retrieve_jobs_by_jobs_id(id=id)
    return APIResponse(status_code=200, data=items, detail="Job item fetched successfully")


@router.post(
    "/",
    response_model= APIResponse[Any],
)
async def post_new_jobs(
    data: JobsBase = Body(
        ...,
        openapi_examples={
            "post_job": {
                "summary": "Client Job Posting Example",
                "description": (
                    "Example payload for a **Client** posting a new job. "
                    "The client specifies the project title, category, budget, "
                    "timeline, and job details. "
                    "System-generated fields (e.g., `client_id`, `admin_approved`, "
                    "`break_down`, `status`, `date_created`, `last_updated`) are "
                    "automatically filled by the backend.\n\n"
                    "⚠️ **REQUIRES CLIENT TOKENS**"
                ),
                "value": {
                    "project_title": "E-commerce Website Development",
                    "primary_area_of_expertise": "Web Devlopment",  # ✅ match Enum exactly
                    "budget": 2500,
                     
                    "description": "Develop a full-featured e-commerce website with shopping cart and payment integration.",
                    "timeline": {
                        "start_date": 1696224000,   # Unix timestamp for project start
                        "deadline": 1698816000      # Unix timestamp for deadline
                    }
                },
            }
        },
    ),
    token: accessTokenOut = Depends(verify_client_token),
):

    job_data = JobsCreate(**data.model_dump(), client_id=token.userId)
    result = celery_app.send_task(name="celery_worker.add_new_job",args=[job_data.model_dump()])
    return APIResponse(status_code=200, data=f"{result}", detail="Job posted successfully")

@router.post("/reject/{job_id}")
async def admin_reject_new_job_posting(
    job_id: str,
    job_data: JobsUpdate = Body(
        openapi_examples={
            "reject_job": {
                "summary": "Reject Job Example ",
                "description": (
                    "Example payload for an **Admin** rejecting a job posting. "
                    "The admin sets `admin_approved` to `false` and states reasons for rejection, "
                   
                    "⚠️**REQUIRES ADMIN TOKENS**"
                ),
                "value": {
                    "admin_approved": False,
                    "rejection_reason": "This user doesn't meet the expectation needed on the platform",
                },
            }
        }
    ),
        token: accessTokenOut = Depends(verify_admin_token),
):
    old_data =await retrieve_jobs_by_jobs_id(id=job_id)
    if old_data.admin_approved == False:
        data = JobsUpdate(admin_approved=False,rejection_reason=job_data.rejection_reason,status=JobStatus.rejected)
        returned_job_stuff = await update_jobs_by_id(jobs_id=job_id,jobs_data=data)
        remove_time = datetime.now() + timedelta(hours=20)
        scheduler.add_job(remove_jobs, "date", run_date=remove_time, args=[job_id],misfire_grace_time=31536000)
        return APIResponse(status_code=200,data=returned_job_stuff,detail="Successfully approved job-posting")
    elif old_data.admin_approved==True:
        return APIResponse(status_code=400,detail="admin approved object is supposed to be false")

@router.post("/propose/{job_id}")
async def admin_sending_client_job_proposal(
    job_id: str,
    job_data: JobsUpdate = Body(
        openapi_examples={
            "proposal": {
                "summary": "Send Job Proposal Example",
                "description": (
                    "Example payload for an **Admin** sending a proposal about a job posting. "
                    "The admin sets `admin_approved` to `true` and applies charges and tax. "
                    "⚠️ **REQUIRES ADMIN TOKENS**"
                ),
                "value": {
                    "agent": {
                        "id": "67514f4bf011bc33ab3c25e9",
                        "email": "agent@example.com",
                        "password": "$2b$12$ZW5jcnlwdGVkLWhhc2gtcGFzc3dvcmQ",
                        "full_name": "John Doe",
                        "phone_number": "+2348012345678",
                        "certificate_url": [
                            "https://example.com/certificates/cert1.pdf",
                            "https://example.com/certificates/cert2.pdf"
                        ],
                        "video_url": "https://example.com/videos/intro.mp4",
                        "personality_url": "https://example.com/personality/assessment.pdf",
                        "primary_area_of_expertise": "software_development",
                        "years_of_experience": 5,
                        "three_most_commonly_used_tools_or_platforms": [
                            "Figma",
                            "Slack",
                            "Jira"
                        ],
                        "available_hours_agent_can_commit": "20_hours_per_week",
                        "time_zone": "+01:00",
                        "portfolio_link": "https://portfolio.example.com/john-doe",
                        "is_agent_open_to_calls_and_video_meetings": True,
                        "does_agent_have_working_computer": True,
                        "does_agent_have_stable_internet": True,
                        "is_agent_comfortable_with_time_tracking_tools": True,
                        "date_created": 1763115507,
                        "last_updated": 1763115507
                    },
                    "timeline": {
                        "start_date": int(time.time()),
                        "deadline": int(time.time())
                    },
                    "proposal": "Some text the admin sends to the client",
                    "break_down": {
                        "service": 1000,
                        "Charges": 7,  # 7%
                        "Tax": 10      # 10%
                    }
                }
            }
        }
    ),
    token: accessTokenOut = Depends(verify_admin_token),
):
    
    old_data =await retrieve_jobs_by_jobs_id(id=job_id)
    if old_data.admin_approved == False and old_data.client_approved==False:

        data = JobsUpdate(admin_approved=True, break_down=job_data.break_down,recommended_agents=job_data.recommended_agents,proposal=job_data.proposal)
        returned_job_stuff =await update_jobs_by_id(jobs_id=job_id,jobs_data=data)
        
        return APIResponse(status_code=200,data=returned_job_stuff,detail="Successfully approved job-posting")
    else: raise HTTPException(status_code=409,detail="admin has approved already")
    
    
    

@router.patch("/client/accept-proposal/{job_id}")
async def client_accepting_admin_job_proposal(
    job_id: str,
    job_data: JobsUpdate = Body(
        openapi_examples={
            "accept_proposal": {
                "summary": "Accept Job Proposal Example ",
                "description": (
                    "Example payload for a **client** Accepting a proposal about a job posting. "
                    "The Client sets `client_approved` to `true` and selects Agents To Work With "
                    
                    "⚠️**REQUIRES CLIENT TOKENS**"
                ),
                "value": {
                    "client_approved": True,
                    "selected_agents":["agent1","agent2","agent3"],
                     
                     
                },
            }
        }
    ),
        token: accessTokenOut = Depends(verify_client_token),
):
    jobs  =await get_jobs(filter_dict={"client_id":token.userId,"_id":ObjectId(job_id)})
    if jobs:
        data = JobsUpdate(client_approved=True, break_down=job_data.break_down,recommended_agents=job_data.recommended_agents,proposal=job_data.proposal,status=JobStatus.active) 
        returned_job_stuff =await update_jobs_by_id(jobs_id=job_id,jobs_data=data)
        return APIResponse(status_code=200,data=returned_job_stuff,detail="Successfully approved job-posting")
    

@router.patch("/client/reject-proposal/{job_id}")
async def client_rejecting_admin_job_proposal(
    job_id: str,
    job_data: JobsUpdate = Body(
        openapi_examples={
            "reject_proposal": {
                "summary": "Reject Job Proposal Example ",
                "description": (
                    "Example payload for a **client** Rejecting a proposal about a job posting. "
                    "The Client sets `client_approved` to `false` and Writes Rejection Reason "
                    
                    "⚠️**REQUIRES CLIENT TOKENS**"
                ),
                "value": {
                    "client_approved": False,
                    "client_rejection_reason":"Just because of the price and I didn't like the agents you showed me",
                },
            }
        }
    ),
        token: accessTokenOut = Depends(verify_client_token),
):
    jobs  =await get_jobs(filter_dict={"client_id":token.userId,"_id":ObjectId(job_id)})
    if jobs:
        data = JobsUpdate(client_approved=False,client_rejection_reason=job_data.client_rejection_reason, break_down=job_data.break_down,recommended_agents=job_data.recommended_agents,proposal=job_data.proposal,status=JobStatus.active) 
        returned_job_stuff =await update_jobs_by_id(jobs_id=job_id,jobs_data=data)
        return APIResponse(status_code=200,data=returned_job_stuff,detail="Successfully approved job-posting")
    
    
    

@router.post("/client/set-meeting/")
async def client_setting_meeting(
    
    job_meeting_data: JobMeeting = Body(
        openapi_examples={
            "Set_meeting": {
                "summary": "Setting Job meeting Example ",
                "description": (
                    "Example payload for a **client** setting a meeting about a job posting with an agent. "
                    "The Client sets `client_approved` to `false` and Writes Rejection Reason "
                    
                    "⚠️**REQUIRES CLIENT TOKENS**"
                ),
                "value": {
                    "job_id": "job_sadsdsaa",
                    "agent_id":"agent_sadsdsaa",
                    "meeting_time":int(time.time())
                },
            }
        }
    ),
        token: accessTokenOut = Depends(verify_client_token),
):
    jobs  =await get_jobs(filter_dict={"client_id":token.userId,"_id":ObjectId(job_meeting_data.job_id)})
    if jobs:
         for agent in jobs.recommended_agents:
            if agent.id ==job_meeting_data.agent_id:
                client_alert =AlertsBase(user_type=UserTypes.client,user_id=token.userId,priority=PriorityStatus.very_high,alert_type=AlertType.meeting,alert_title=f"Client Created A Meeting to discuss the job: {jobs.project_title}",alert_description=f"Client Created A Meeting to discuss the job: {jobs.project_title}, {jobs.description}, {jobs.budget}",alert_primary_action="Mark as Read",alert_secondary_action="Cancel")
                agent_alert =AlertsBase(user_type=UserTypes.agent,user_id=job_meeting_data.agent_id,priority=PriorityStatus.very_high,alert_type=AlertType.meeting,alert_title=f"Client Created A Meeting to discuss the job: {jobs.project_title}",alert_description=f"Client Created A Meeting to discuss the job: {jobs.project_title}, {jobs.description}, {jobs.budget}",alert_primary_action="Mark as Read",alert_secondary_action="Cancel")
                admin_alert =AlertsBase(user_type=UserTypes.admin,user_id="admin_id",priority=PriorityStatus.very_high,alert_type=AlertType.meeting,alert_title=f"Client Created A Meeting to discuss the job: {jobs.project_title}",alert_description=f"Client Created A Meeting to discuss the job: {jobs.project_title}, {jobs.description}, {jobs.budget}",alert_primary_action="Mark as Read",alert_secondary_action="Cancel")
                # Make the db functions go to the queue
                # new_client_alert = await add_alerts(alerts_data=client_alert)
                celery_app.send_task("celery_worker.add_new_alert",args=[client_alert.model_dump()])
                celery_app.send_task("celery_worker.add_new_alert",args=[agent_alert.model_dump()])
                celery_app.send_task("celery_worker.add_new_alert",args=[admin_alert.model_dump()])
                
                
                return APIResponse(status_code=200,data="Meeting has been set you will receive a notification soon",detail="Successfully set job-meeting")
            
         raise HTTPException(status_code=403,detail="This agent wasn't part of the recommended agents so you cant setup a meeting with them")

    else:
        raise HTTPException(status_code=400,detail="This Job doesn't exist")
    
    
    
@router.patch("/mark-completed/{job_id}", response_model=APIResponse[JobsOut],dependencies=[Depends(verify_client_token)])
async def client_should_use_this_to_mark_job_as_complete(job_id:str,token:accessTokenOut=Depends(verify_client_token)):
    jobs  =await get_jobs(filter_dict={"client_id":token.userId,"_id":ObjectId(job_id)})
    if jobs:
          
        update_data = JobsUpdate(isCompleted=True,status=JobStatus.completed) 
        item = await update_jobs_by_id(jobs_id=job_id,jobs_data=update_data,status=JobStatus.completed)
        
        return APIResponse(status_code=200, data=item, detail="applications updated successfully")
    return APIResponse(status_code=403,data="User Doesn't have any job with this job id",detail="Unauthorized Access")


