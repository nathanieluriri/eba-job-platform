
from fastapi import APIRouter, HTTPException, Query, status, Path,Depends
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
from security.auth import verify_agent_token,accessTokenOut


router = APIRouter(prefix="/agents", tags=["Agents"])



@router.get("/me",response_model_exclude_none=True, dependencies=[Depends(verify_agent_token)],response_model=APIResponse[UserOut])
async def get_my_agents(token:accessTokenOut =Depends(verify_agent_token)):
    
    items = await retrieve_agent_by_agent_id(id=token.userId)
    items.password=""
    return APIResponse(status_code=200, data=items, detail="agents items fetched")

@router.post("/login", response_model=APIResponse[UserOut])
async def login_user(user_data:UserLogin):
    items = await authenticate_agent(user_data=user_data)
    items.password=""
    return APIResponse(status_code=200, data=items, detail="Fetched successfully")
