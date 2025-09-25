
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends
from typing import List
from schemas.response_schema import APIResponse
from schemas.client import (
    ClientCreate,
    ClientOut,
    ClientBase,
    ClientUpdate,
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
    update_client,
    authenticate_client
)
from security.auth import verify_client_token,accessTokenOut



router = APIRouter(prefix="/clients", tags=["Clients"])




@router.get("/me",response_model_exclude_none=True,dependencies=[Depends(verify_client_token)], response_model=APIResponse[UserOut])
async def get_my_clients(token:accessTokenOut = Depends(verify_client_token)):
    items = await retrieve_client_by_client_id(id=token.userId)
    items.password=""
    return APIResponse(status_code=200, data=items, detail="clients items fetched")

@router.post("/login", response_model=APIResponse[UserOut])
async def login_user(user_data:UserLogin):
    items = await authenticate_client(user_data=user_data)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")
