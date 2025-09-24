
from fastapi import APIRouter, HTTPException, Query, status, Path
from typing import List
from schemas.response_schema import APIResponse
from schemas.agent import (
    AgentCreate,
    AgentOut,
    AgentBase,
    AgentUpdate,
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
    update_agent,
    authenticate_agent
)

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/", response_model=APIResponse[List[AgentOut]])
async def list_agents():
    items = await retrieve_agents()
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")

@router.get("/me", response_model=APIResponse[AgentOut])
async def get_my_agents(id: str = Query(..., description="agent ID to fetch specific item")):
    items = await retrieve_agent_by_agent_id(id=id)
    return APIResponse(status_code=200, data=items, detail="agents items fetched")

@router.post("/login", response_model=APIResponse[UserOut])
async def login_user(user_data:UserLogin):
    items = await authenticate_agent(user_data=user_data)
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")
