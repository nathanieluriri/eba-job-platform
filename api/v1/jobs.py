
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends,Body
from typing import List
from schemas.response_schema import APIResponse
from security.auth import verify_client_token,accessTokenOut,verify_agent_token,verify_admin_token
from schemas.jobs import (
    JobsCreate,
    JobsOut,
    JobsBase,
    PriceBreakDown,
    JobsUpdate,
)
from services.jobs_service import (
    add_jobs,
    remove_jobs,
    retrieve_jobss,
    retrieve_jobs_by_jobs_id,
    update_jobs_by_id,
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



@router.get(
    "/admin/{start}/{stop}",
    description="⚠️**REQUIRES ADMIN TOKENS**",
    response_model=APIResponse[List[JobsOut]]
)
async def list_jobss(
    start: int = Path(
        
        description="Start index (default: 0)",
        examples={
            "example_start": {
                "summary": "Start at the first job",
                "description": "This sets the starting index of the jobs list to fetch. ⚠️ **REQUIRES ADMIN TOKENS**",
                "value": 0
            }
        }
    ),
    stop: int = Path(
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
    response_model=APIResponse[JobsOut],
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
                    "required skills, timeline, and job details. "
                    "System-generated fields (e.g., `client_id`, `admin_approved`, "
                    "`break_down`, `status`, `date_created`, `last_updated`) are "
                    "automatically filled by the backend.\n\n"
                    "⚠️ **REQUIRES CLIENT TOKENS**"
                ),
                "value": {
                    "project_title": "E-commerce Website Development",
                    "category": "Web Devlopment",  # ✅ match Enum exactly
                    "budget": 2500,
                    "description": "Develop a full-featured e-commerce website with shopping cart and payment integration.",
                    "requirement": "Experience with React.js, Node.js, and PostgreSQL.",
                    "skills_needed": "Web Devlopment",  # ✅ match Enum exactly
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
    items = await add_jobs(jobs_data=job_data)
    return APIResponse(status_code=200, data=items, detail="Job posted successfully")


@router.post("/approve/{job_id}")
async def approve_new_job_posting(
    job_id: str,
    job_data: JobsUpdate = Body(
        openapi_examples={
            "approve_job": {
                "summary": "Approve Job Example ",
                "description": (
                    "Example payload for an **Admin** approving a job posting. "
                    "The admin sets `admin_approved` to `true` and applies charges and tax, "
                    "both represented as percentages."
                    "⚠️**REQUIRES ADMIN TOKENS**"
                ),
                "value": {
                    "admin_approved": True,
                    "break_down": {
                        "Charges": 10,   # 10% service charge
                        "Tax": 7         # 7% tax
                    }
                },
            }
        }
    )
):
    if job_data.admin_approved is True:
        JobsUpdate(admin_approved=True, break_down=job_data.break_down)
        await update_jobs_by_id(jobs_id=job_id)