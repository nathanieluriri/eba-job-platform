
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends,Body
from core.redis_cache import get_cached_value,cache_with_expiry
from typing import List,Annotated
from services.utils import generate_random_string,generate_random_string_digits_only
from security.auth import verify_admin_token,verify_token
from schemas.response_schema import APIResponse
from schemas.agent import (
    AgentCreate,
    AgentOut,
    AgentBase,
    AgentUpdate,
    PasswordResetInStep1,
    PasswordResetInStep2,
    PasswordResetOutStep1
)
from schemas.user_schema import (
    UserCreate,
    UserOut,
    UserBase,
    UserUpdate,
    UserLogin
)
from services.agent_service import (
    add_agent,
    remove_agent,
    retrieve_agents,
    retrieve_agent_by_agent_id,
    update_agent_by_id,
    authenticate_agent
)
from security.auth import verify_agent_token,accessTokenOut


router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get(
    "/{start}/{stop}", 
    response_model=APIResponse[List[UserOut]],
    response_model_exclude_none=True,
    dependencies=[Depends(verify_token)]
)
async def list_agents(
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
    items = await retrieve_agents(start=0, stop=100)
    
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")



@router.get("/me",response_model_exclude_none=True, dependencies=[Depends(verify_agent_token)],response_model=APIResponse[UserOut])
async def get_my_agents(token:accessTokenOut =Depends(verify_agent_token)):
    
    items = await retrieve_agent_by_agent_id(id=token.userId)
    items.password=""
    return APIResponse(status_code=200, data=items, detail="agents items fetched")

@router.post("/login", response_model=APIResponse[UserOut])
async def login_agent(user_data: UserLogin = Body(
        openapi_examples={
            "agent_login": {
                "summary": "Agent Login Example",
                "description": "Login request for a **Agent** using email and password.",
                "value": {
                    "email": "agent@example.com",
                    "password": "agentpassword456"
                },
            },
           
        }
    )
):
    items = await authenticate_agent(user_data=user_data)
    items.password=""
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")





@router.post(
    "/get-reset-token",
    response_model=APIResponse[PasswordResetOutStep1],
)
async def send_reset_token(
    user_data: PasswordResetInStep1 = Body(
        ...,
        openapi_examples={
            "valid_request": {
                "summary": "📧 Request reset token",
                "description": "Generate a **password reset token** for a client.",
                "value": {
                    "email": "client@example.com"
                },
            },
            "unregistered_email": {
                "summary": "❌ Unregistered email",
                "description": """
                When the provided email does not exist in the system.  
                The server responds with a **404 error**.
                """,
                "value": {
                    "email": "notfound@example.com"
                },
            },

        },
    ),
):
    """
    Generate and cache a reset token for a client.
    """
    client = await retrieve_agents(filter={"email": user_data.email})
    if client:
        reset_token = generate_random_string()
        cache_with_expiry(key=reset_token, value="123456", ttl=240)
        return APIResponse(
            status_code=200,
            data=PasswordResetOutStep1(reset_token=reset_token),
            detail="Reset Token sent successfully",
        )
    else:
        raise HTTPException(status_code=404, detail="user not found")
    
    
@router.patch(
    "/reset-password",
    response_model=APIResponse[UserOut],
)
async def reset_password(
    user_data: PasswordResetInStep2 = Body(
        ...,
        openapi_examples={
            "valid_request": {
                "summary": "🔑 Reset agent password",
                "description": "Reset an agent's password using a **reset token** and **OTP**.",
                
                "value": {
                    "reset_token": "reset_token:WKyklwccxrE6fYKg;email:agent1@example.com",
                    "otp": "123456",
                    "new_password": "MyNewSecurePass123"
                },
            },
            
        },
    ),
):
    """
    Reset an agent's password using a reset token and OTP.
    """
    value = get_cached_value(key=user_data.reset_token)
    long_string = user_data.reset_token

    # Extract email from reset token format
    parts = long_string.split(';email:')
    email_and_quote = parts[1]  # e.g. 'agent@example.com"'
    email = email_and_quote.rstrip('"')

    if value == user_data.otp:
        agents = await retrieve_agents(filter={"email": email})
        agent = agents[0]
        user_new_password = UserUpdate(password=user_data.new_password)

        if agent:
            agent = await update_agent_by_id(agent_id=agent.id, agent_data=user_new_password)
            return APIResponse(
                status_code=200,
                data=agent,
                detail=f"Successfully updated {agent.email} password, try to log in {agent.full_name}"
            )
        else:
            raise HTTPException(status_code=404, detail="Agent Not Found")

    raise HTTPException(status_code=401, detail="Invalid OTP")