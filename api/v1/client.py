
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends,Body
from core.redis_cache import cache_with_expiry, get_cached_value
from services.utils import generate_random_string
from typing import List,Annotated
from security.auth import verify_token
from schemas.response_schema import APIResponse
from schemas.client import (
    ClientCreate,
    ClientOut,
    ClientBase,
    ClientUpdate,
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
from services.client_service import (
    add_client,
    remove_client,
    retrieve_clients,
    retrieve_client_by_client_id,
    update_client_by_id,
    authenticate_client
)
from security.auth import verify_client_token,accessTokenOut



router = APIRouter(prefix="/clients", tags=["Clients"])




@router.get(
    "/{start}/{stop}", 
    response_model=APIResponse[List[UserOut]],
    response_model_exclude_none=True,
    dependencies=[Depends(verify_token)]
)
async def list_clients(
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
    items = await retrieve_clients(start=0, stop=100)
    
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")


@router.get(
    "/me",
    response_model_exclude_none=True,
    dependencies=[Depends(verify_client_token)],
    response_model=APIResponse[UserOut],
    description=(
        "Retrieve the profile information of the currently authenticated **Client**. "
        "This endpoint uses the provided client token to identify the requesting user "
        "and returns their account details. The `password` field is always excluded "
        "from the response for security reasons. "
        "\n\n⚠️ **Requires valid Client authentication tokens.**"
    )
)
async def get_my_clients(token: accessTokenOut = Depends(verify_client_token)):
    items = await retrieve_client_by_client_id(id=token.userId)
    items.password = ""
    return APIResponse(status_code=200, data=items, detail="Client profile fetched successfully")



@router.post(
    "/login",
    response_model=APIResponse[UserOut],
    description=(
        "Authenticate a user (client role) with their login credentials. "
        "If the credentials are valid, this endpoint returns the user profile "
        "along with authentication tokens required for future requests. "
        "\n\n⚠️ Ensure you store and handle tokens securely."
    )
)
async def login_client(
    user_data: UserLogin = Body(
        openapi_examples={
            "client_login": {
                "summary": "Client Login Example",
                "description": "Login request for a **Client** using email and password.",
                "value": {
                    "email": "client@example.com",
                    "password": "securepassword123"
                },
            },
           
        }
    )
):
    items = await authenticate_client(user_data=user_data)
    return APIResponse(status_code=200, data=items, detail="Login successful")

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
                "description":( 
                    "Generate a **password reset token** for a client."
                "The token will be cached temporarily (TTL = 240 seconds).  "
                "1. Provide your registered email."
                "2. If valid, a reset token is generated and cached."
                "3. The token is sent back in the response (and typically emailed)."
               " 4. The token expires after a short time."),
                "value": {
                    "email": "client@example.com"
                },
            },
          
            "response_not_found": {
                "summary": "🚨 Error response example",
                "description": "When the email is not found in the system.",
                "value": {
                    "detail": "user not found"
                },
            },
        },
    ),
):
    """
    Generate and cache a reset token for a client.
    """
    client = await retrieve_clients(filter={"email": user_data.email})
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
                "summary": "🔑 Reset client password",
                "description": "Reset a client's password using a **reset token** and **OTP**.",
                
                "value": {
                    "reset_token": "reset_token:WKyklwccxrE6fYKg;email:client1@example.com",
                    "otp": "123456",
                    "new_password": "MyNewSecurePass123"
                },
            },
            
        },
    ),
):
    """
    Reset an client's password using a reset token and OTP.
    """
    value = get_cached_value(key=user_data.reset_token)
    long_string = user_data.reset_token

    # Extract email from reset token format
    parts = long_string.split(';email:')
    email_and_quote = parts[1]  # e.g. 'agent@example.com"'
    email = email_and_quote.rstrip('"')

    if value == user_data.otp:
        clients = await retrieve_clients(filter={"email": email})
        client = clients[0]
        user_new_password = UserUpdate(password=user_data.new_password)

        if client:
            client = await update_client_by_id(client_id=client.id, client_data=user_new_password)
            return APIResponse(
                status_code=200,
                data=client,
                detail=f"Successfully updated {client.email} password, try to log in {client.full_name}"
            )
        else:
            raise HTTPException(status_code=404, detail="client Not Found")

    raise HTTPException(status_code=401, detail="Invalid OTP")