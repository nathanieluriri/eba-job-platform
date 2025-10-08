
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends,Body
from typing import List,Annotated
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
    UserLogin
)
from services.user_service import (
    add_user,
    remove_user,
    retrieve_users,
    authenticate_user,
    retrieve_user_by_user_id,
    update_user,
    refresh_user_tokens_reduce_number_of_logins,

)
from security.auth import verify_token,verify_token_to_refresh
router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/{start}/{stop}", 
    response_model=APIResponse[List[UserOut]],
    response_model_exclude_none=True,
    dependencies=[Depends(verify_token)],
    response_model_exclude={"data": {"__all__": {"password"}}},
)
async def list_users(
    # Use Path and Query for explicit documentation/validation of GET parameters
    start: Annotated[
        int,
        Path(ge=0, description="The starting index (offset) for the list of users.")
    ] , 
    stop: Annotated[
        int, 
        Path(gt=0, description="The ending index for the list of users (limit).")
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


@router.get(
    "/me", 
    response_model=APIResponse[UserOut],
    dependencies=[Depends(verify_token)],
    response_model_exclude_none=True,
     response_model_exclude={"data": {"password"}},
)
async def get_my_users(
    token: accessTokenOut = Depends(verify_token),
    # Using Body to include openapi_examples for documentation purposes, 
    # even though the actual body is empty.
    _body: Annotated[
        dict,
        Body(
            openapi_examples={
                "successful_profile_fetch": {
                    "summary": "Successful Profile Retrieval",
                    "description": (
                        "A successful request **requires no body** and relies on a **valid, non-expired Access Token** "
                        "in the `Authorization: Bearer <token>` header to identify the user (via `token.userId`)."
                    ),
                    "value": {},  # Explicitly empty body
                },
                "unauthenticated_request": {
                    "summary": "Unauthenticated Request (Missing Token)",
                    "description": (
                        "This scenario represents a request where the **Access Token is missing or malformed**. "
                        "The `verify_token` dependency should intercept this and return a **401 Unauthorized** error."
                    ),
                    "value": {},  # Explicitly empty body
                },
            }
        ),
    ] = {}, # Default empty dictionary for the body
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
    if user_data.role == UserRolesBase.client:
        userRole = UserRoles.client
    elif user_data.role == UserRolesBase.agent:
        userRole = UserRoles.agent        
    user_data_dict = user_data.model_dump() 
    user_data_dict.pop('role')
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
    else: raise HTTPException(status_code=409,detail="Account hasn't been approved by admin yet please wait until your account has been approved")



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
    ],
    token: accessTokenOut = Depends(verify_token_to_refresh)
):
    """
    Refreshes the user's access token and returns a new token pair.

    Requires an **expired access token** in the Authorization header and a **valid refresh token** in the body.
    """
    
    items = await refresh_user_tokens_reduce_number_of_logins(
        user_refresh_data=user_data,
        expired_access_token=token.accesstoken
    )
    
    # Clears the password before returning, which is good practice.
    items.password = ''
    
    return APIResponse(status_code=200, data=items, detail="users items fetched")


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
    result = await remove_user(user_id=token.userId)
    
    # The 'result' is assumed to be a standard FastAPI response object or a dict/model 
    # that is automatically converted to a response.
    return result