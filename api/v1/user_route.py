
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends,Body
from typing import List,Annotated
from datetime import datetime,timedelta
from core.scheduler import scheduler
from pydantic import ValidationError
from schemas.response_schema import APIResponse
from schemas.tokens_schema import accessTokenOut
from schemas.user_schema import (
    UserCreate,
    UserOut,
    UserBase,
    UserUpdate,
    UserRefresh,
    UserRoleBody,
    UserRoles,
    UserRolesBase,
    UserLogin,
    UserRejection,
    UserUpdateRequest
    
)
from schemas.agent import (
    AgentBase
)
from schemas.client import(
    ClientBase
)
from services.user_service import (
    add_user,
    remove_user,
    retrieve_users,
    authenticate_user,
    retrieve_user_by_user_id,
    update_user_by_id,
    refresh_user_tokens_reduce_number_of_logins,

)
from services.utils import format_pydantic_errors
from security.auth import verify_admin_token,verify_token_to_refresh,verify_token
router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/", 
    response_model=APIResponse[List[UserOut]],
    response_model_exclude_none=True,
    dependencies=[Depends(verify_admin_token)],
    response_model_exclude={"data": {"__all__": {"password"}}},
)
async def list_users(
    # Use Path and Query for explicit documentation/validation of GET parameters
    start: Annotated[
        int,
        Query( ge=0, description="The starting index (offset) for the list of users.")
    ] , 
    stop: Annotated[
        int, 
        Query( gt=0, description="The ending index for the list of users (limit).")
    ] 
):
    """
    **ADMIN ONLY:** Retrieves a paginated list of all registered users.

    **Authorization:** Requires a **valid Access Token** (Admin role) in the 
    `Authorization: Bearer <token>` header.

    ### Examples (Illustrative URLs):

    * **First Page:** `/users/0/50` (Start at index 0, retrieve up to 50 users)
    * **Second Page:** `/users/50/100` (Start at index 50, retrieve up to 50 users)
    * **Default:** `/users/0/100` (Default behavior if parameters are omitted or set to default)
    """
    
    # Note: The code below overrides the path parameters with hardcoded defaults (0, 100).
    # You should typically use the passed parameters: 
    # items = await retrieve_users(start=start, stop=stop)
    
    # Using the hardcoded values from your original code:
    items = await retrieve_users(start=0, stop=100)
    
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")



@router.patch(
    "/{user_id}/reject", 
    response_model=APIResponse[UserOut],
    response_model_exclude_none=True,
    dependencies=[Depends(verify_admin_token)],
    response_model_exclude={"data": {"password"}},
)

async def reject_users_either_client_or_agents(
    # Use Path and Query for explicit documentation/validation of GET parameters

    user_id: Annotated[
        str,
        Path(description="user id. could be a user id for any role client or agent")
    ] , 
    
        user:UserRejection=Body(
        openapi_examples={
            "reject_user": {
                "summary": "Reject user Example ",
                "description": (
                    "Example payload for an **Admin** rejecting a user from the platform. "
                    "The admin sets `admin_approved` to `false` and states reasons for rejection, "
                   
                    "⚠️**REQUIRES ADMIN TOKENS**"
                ),
                "value": {
                    "admin_approved": False,
                    "rejection_reason": "This user doesn't meet the expectation needed on the platform",
                },
            }
        }),
    
):
    """
    **ADMIN ONLY:** Approves any user using user id.

    **Authorization:** Requires a **valid Access Token** (Admin role) in the 
    `Authorization: Bearer <token>` header.

    ### Examples (Illustrative URLs):

    * **Reject user:** `/users/034910212/reject` 

    """
    
   
    user_data =await retrieve_user_by_user_id(id=user_id)
    if user_data.admin_approved!=True:
        data =UserUpdate(admin_approved=False,rejection_reason=user.rejection_reason)
        items = await update_user_by_id(user_id=user_id,user_data=data)
        
        remove_time = datetime.now() + timedelta(days=3)
        if user_data.rejection_reason==None:
            scheduler.add_job(remove_user, "date", run_date=remove_time, args=[user_id],misfire_grace_time=31536000)
        return APIResponse(status_code=200, data=items, detail="Rejected user registration successfully")
    else: return APIResponse(status_code=400, data=user_data, detail="Failed to reject user registration successfully because user has already been approved")





@router.patch(
    "/{user_id}/approve", 
    response_model=APIResponse[UserOut],
    response_model_exclude_none=True,
    dependencies=[Depends(verify_admin_token)],
    response_model_exclude={"data": {"password"}},
)
async def approve_users_either_client_or_agents(
    # Use Path and Query for explicit documentation/validation of GET parameters
    user_id: Annotated[
        str,
        Path(description="user id. could be a user id for any role client or agent")
    ] , 
    
):
    """
    **ADMIN ONLY:** Approves any user using user id.

    **Authorization:** Requires a **valid Access Token** (Admin role) in the 
    `Authorization: Bearer <token>` header.

    ### Examples (Illustrative URLs):

    * **Approve user:** `/users/034910212/approve` 

    """
    
    # Note: The code below overrides the path parameters with hardcoded defaults (0, 100).
    # You should typically use the passed parameters: 
    # items = await retrieve_users(start=start, stop=stop)
    
    # Using the hardcoded values from your original code:
    data =UserUpdate(admin_approved=True)
    items = await update_user_by_id(user_id=user_id,user_data=data)
    
    return APIResponse(status_code=200, data=items, detail="Approved user registration successfully")


@router.get(
    "/me", 
    response_model=APIResponse[UserOut],
    response_model_exclude_none=True,
     response_model_exclude={"data": {"password"}},
)
async def get_my_users(
    token: accessTokenOut = Depends(verify_token),

):
    """
    Retrieves the profile information for the currently authenticated user.

    The user's ID is automatically extracted from the valid Access Token 
    in the **Authorization: Bearer <token>** header.
    """
    
    items = await retrieve_user_by_user_id(id=token.userId)
    return APIResponse(status_code=200, data=items, detail="users items fetched")





@router.post("/signup", response_model_exclude={"data": {"password"}},response_model_exclude_none=True, response_model=APIResponse[str])
async def signup_new_user(
    user_data: Annotated[
        UserBase,
        Body(
            openapi_examples={
                "client_signup": {
                    "summary": "Client Signup Example",
                    "description": "Example payload for a **Client** registering on the platform.",
                    "value": {
                        "email": "client@example.com",
                        "password": "securepassword123",
                        "role": "client",
                        "phone_number": "+1234567890",
                        "certificate_url": ["https://example.com/cert1.pdf"],
                        "video_url": "https://example.com/intro.mp4",
                        "personality_url": "https://example.com/personality.pdf",
                        "company_name": "Tech Solutions Ltd",
                        "company_email": "contact@techsolutions.com",
                        "company_address": "123 Business Street, City",
                        "full_name": "Alice Johnson",
                        "services": ["Mobile Development", "Content Writing"],
                        "client_reason_for_signing_up": "Just hire me someone",
                        "client_need_agent_work_hours_to_be": "both",
                    },
                },
                "agent_signup": {
                    "summary": "Agent Signup Example",
                    "description": "Example payload for an **Agent** registering on the platform.",
                    "value": {
                        "email": "agent@example.com",
                        "full_name": "Alice Johnson",
                        "password": "agentpassword456",
                        "role": "agent",
                        "phone_number": "+1987654321",
                        "certificate_url": ["https://example.com/cert2.pdf"],
                        "video_url": "https://example.com/agent_intro.mp4",
                        "personality_url": "https://example.com/agent_personality.pdf",
                        "primary_area_of_expertise": "Mobile Development",
                        "years_of_experience": 5,
                        "three_most_commonly_used_tools_or_platforms": [
                            "Google Analytics",
                            "HubSpot",
                            "Excel"
                        ],
                        "available_hours_agent_can_commit": 80,
                        "time_zone": "UTC+01:00",
                        "portfolio_link": "https://portfolio.example.com/agent123",
                        "is_agent_open_to_calls_and_video_meetings": True,
                        "does_agent_have_working_computer": True,
                        "does_agent_have_stable_internet": True,
                        "is_agent_comfortable_with_time_tracking_tools": True,
                    },
                },
            }
        ),
    ]
):
    try:
        if user_data.role == UserRolesBase.client:
            user = ClientBase(**user_data.model_dump()) # Pydantic ValidationError raised here
            userRole = UserRoles.client
        elif user_data.role == UserRolesBase.agent:
            user = AgentBase(**user_data.model_dump()) # Pydantic ValidationError raised here
            userRole = UserRoles.agent
    except ValidationError as e:
        # **This explicit try/except is usually NOT necessary in FastAPI**
        # But if you want a custom 422 format or need to log, you'd handle it here.
        # Otherwise, the error bubbles up and FastAPI handles it automatically.
        readable_detail = format_pydantic_errors(e.errors())
        raise HTTPException(
            status_code=422,
           
            detail= readable_detail# e.errors() provides the structured pydantic error list
        )

        
    user_data_dict = user.model_dump() 

    new_user = UserCreate(
        role=userRole,
        **user_data_dict
    )
    items = await add_user(user_data=new_user)
    return APIResponse(status_code=200, data="Admin has to Approve account before you can use it. ", detail="Fetched successfully")

@router.post("/login", response_model_exclude={"data": {"password"}}, response_model_exclude_none=True,response_model=APIResponse[UserOut])
async def login_user(
    user_data: Annotated[
        UserLogin,
        Body(
            openapi_examples={
                "successful_login": {
                    "summary": "Successful Login",
                    "description": "Standard payload for a successful authentication attempt.",
                    "value": {
                        "email": "user@registered.com",
                        "password": "securepassword123",
                    },
                },
                "unauthorized_login": {
                    "summary": "Unauthorized Login (Wrong Password)",
                    "description": "Payload that would result in a **401 Unauthorized** error due to incorrect credentials.",
                    "value": {
                        "email": "user@registered.com",
                        "password": "wrongpassword999", # Intentionally incorrect
                    },
                },
                "invalid_email_format": {
                    "summary": "Invalid Email Format",
                    "description": "Payload that would trigger a **422 Unprocessable Entity** error due to Pydantic validation failure (not a valid email address).",
                    "value": {
                        "email": "not-an-email-address", # Pydantic will flag this
                        "password": "anypassword",
                    },
                },
            }
        ),
    ]
):
    """
    Authenticates a user with the provided email and password.
    
    Upon success, returns the authenticated user data and an authentication token.
    """
    items = await authenticate_user(user_data=user_data)
    
    
    # The `authenticate_user` function should raise an HTTPException 
    # (e.g., 401 Unauthorized) on failure.
    if items.admin_approved==True:
        return APIResponse(status_code=200, data=items, detail="Fetched successfully")
    else: raise HTTPException(status_code=403,detail="Account hasn't been approved by admin yet please wait until your account has been approved")



@router.post(
    "/refresh",
    response_model=APIResponse[UserOut],
    dependencies=[Depends(verify_token_to_refresh)],
     response_model_exclude={"data": {"password"}},
)
async def refresh_user_tokens(
    user_data: Annotated[
        UserRefresh,
        Body(
            openapi_examples={
                "successful_refresh": {
                    "summary": "Successful Token Refresh",
                    "description": (
                        "The correct payload for refreshing tokens. "
                        "The **expired access token** is provided in the `Authorization: Bearer <token>` header."
                    ),
                    "value": {
                        # A long-lived, valid refresh token
                        "refresh_token": "valid.long.lived.refresh.token.98765"
                    },
                },
                "invalid_refresh_token": {
                    "summary": "Invalid Refresh Token",
                    "description": (
                        "Payload that would fail the refresh process because the **refresh_token** "
                        "in the body is invalid or has expired."
                    ),
                    "value": {
                        "refresh_token": "expired.or.malformed.refresh.token.00000"
                    },
                },
                "mismatched_tokens": {
                    "summary": "Tokens Belong to Different Users",
                    "description": (
                        "A critical security failure example: the refresh token in the body "
                        "does not match the user ID associated with the expired access token in the header. "
                        "This should result in a **401 Unauthorized**."
                    ),
                    "value": {
                        "refresh_token": "refresh.token.of.different.user.77777"
                    },
                },
            }
        ),
    ] ,
    token: accessTokenOut = Depends(verify_token_to_refresh)
):
    """
    Refreshes the user's access token and returns a new token pair.

    Requires an **expired access token** in the Authorization header and a **valid refresh token** in the body.
    """
    try:
        
        
        items = await refresh_user_tokens_reduce_number_of_logins(
            user_refresh_data=user_data,
            expired_access_token=token.accesstoken
        )
        
        # Clears the password before returning, which is good practice.
    
    
        return APIResponse(status_code=200, data=items, detail="users items fetched")
    except Exception as e:
        raise HTTPException(status_code=500,  detail=f"{e}")

@router.patch(
    "/update",
    response_model=APIResponse[UserOut],
    response_model_exclude={"data": {"password"}},

)
async def update_user_details(
    user_update: UserUpdateRequest=Body(
            ...,
            openapi_examples={
                "update_full_name": {
                    "summary": "Update User's Full Name",
                    "description": (
                        "Updates only the user's full name. "
                        "The user's settings remain unchanged."
                    ),
                    "value": {"full_name": "Nathaniel Elo-Oghene Uriri"},
                },
                "update_settings": {
                    "summary": "Update Notification Settings",
                    "description": (
                        "Updates only the user's notification preferences. "
                        "Any unspecified fields remain at their current values."
                    ),
                    "value": {
                        "settings": {
                            "email_notifications": False,
                            "push_notifications": False,
                            "marketing_notifications": True,
                        }
                    },
                },
            }
        ),
    token: accessTokenOut = Depends(verify_token),
):
    """
    Updates the user's details and notification settings.
    Restricted fields like password, admin_approved, and rejection_reason
    cannot be modified here.
    """    

    # ✅ Restrict disallowed fields
    print(type(user_update))
    if getattr(user_update, "admin_approved", None) is not None or getattr(user_update, "rejection_reason", None) is not None:
        raise HTTPException(status_code=400, detail="You cannot modify admin approval fields.")

    if getattr(user_update, "password", None) is not None:
        raise HTTPException(status_code=400, detail="Use the password update endpoint to change your password.")

    # ✅ Update DB record
    try:
        updated_user = await update_user_by_id(
            user_id=token.userId,
            user_data=user_update,
        )

        return APIResponse(status_code=200, data=updated_user, detail="User updated successfully")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")
    
    
@router.delete("/account", dependencies=[Depends(verify_token)], response_model_exclude_none=True)
async def delete_user_account(
    token: accessTokenOut = Depends(verify_token),
    # Use Body to host the openapi_examples, even if the payload is empty
    # We use a simple dictionary here since there is no Pydantic model for the body
    _body: Annotated[
        dict,
        Body(
            openapi_examples={
                "successful_deletion": {
                    "summary": "Successful Account Deletion",
                    "description": (
                        "A successful request **requires no body** and relies entirely on a **valid, non-expired Access Token** "
                        "in the `Authorization: Bearer <token>` header to identify the user."
                    ),
                    "value": {},  # Empty body
                },
                "unauthorized_deletion": {
                    "summary": "Unauthorized Deletion (Invalid Token)",
                    "description": (
                        "This scenario represents a request where the **Access Token is missing, expired, or invalid**. "
                        "The `verify_token` dependency should intercept this and return a **401 Unauthorized**."
                    ),
                    "value": {},  # Empty body
                },
            }
        ),
    ] = {}, # Default empty dictionary for the body
):
    """
    Deletes the account associated with the provided access token.

    The user ID is extracted from the valid Access Token in the Authorization header.
    No request body is required.
    """
    
    
    remove_time = datetime.now() + timedelta(minutes=2)
    scheduler.add_job(remove_user, "date", run_date=remove_time, args=[token.userId],misfire_grace_time=31536000)
    # The 'result' is assumed to be a standard FastAPI response object or a dict/model 
    # that is automatically converted to a response.
    return APIResponse(status_code=200,details="account will be deleted")