
from fastapi import APIRouter, HTTPException, Query, status, Path
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

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("/", response_model=APIResponse[List[ClientOut]])
async def list_clients():
    items = await retrieve_clients()
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/me", response_model=APIResponse[ClientOut])
async def get_my_clients(id: str = Query(..., description="client ID to fetch specific item")):
    items = await retrieve_client_by_client_id(id=id)
    return APIResponse(status_code=200, data=items, detail="clients items fetched")

@router.post("/login", response_model=APIResponse[UserOut])
async def login_user(user_data:UserLogin):
    items = await authenticate_client(user_data=user_data)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")
