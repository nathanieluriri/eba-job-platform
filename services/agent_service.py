# ============================================================================
# AGENT SERVICE
# ============================================================================
# This file was auto-generated on: 2025-09-24 23:31:14 WAT
# It contains  asynchrounous functions that make use of the repo functions 
# 
# ============================================================================

from bson import ObjectId
from fastapi import HTTPException
from typing import List
from repositories.tokens_repo import (
    add_access_tokens,
    add_refresh_tokens,
    
)
from repositories.agent import (
    create_agent,
    get_agent,
    get_agents,
    update_agent,
    delete_agent,
)
from schemas.agent import AgentCreate, AgentUpdate, AgentOut
from schemas.user_schema import UserBase,UserOut
from schemas.tokens_schema import accessTokenCreate,refreshTokenCreate
from security.hash import check_password

async def add_agent(agent_data: AgentCreate) -> AgentOut:
    """adds an entry of AgentCreate to the database and returns an object

    Returns:
        _type_: AgentOut
    """
    return await create_agent(agent_data)


async def remove_agent(agent_id: str):
    """deletes a field from the database and removes AgentCreateobject 

    Raises:
        HTTPException 400: Invalid agent ID format
        HTTPException 404:  Agent not found
    """
    if not ObjectId.is_valid(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID format")

    filter_dict = {"_id": ObjectId(agent_id)}
    result = await delete_agent(filter_dict)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")


async def retrieve_agent_by_agent_id(id: str) -> AgentOut:
    """Retrieves agent object based specific Id 

    Raises:
        HTTPException 404(not found): if  Agent not found in the db
        HTTPException 400(bad request): if  Invalid agent ID format

    Returns:
        _type_: AgentOut
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid agent ID format")

    filter_dict = {"_id": ObjectId(id)}
    result = await get_agent(filter_dict)

    if not result:
        raise HTTPException(status_code=404, detail="Agent not found")

    return result


async def retrieve_agents(filter=None,start=0,stop=100) -> List[AgentOut]:
    """Retrieves AgentOut Objects in a list

    Returns:
        _type_: AgentOut
    """
    return await get_agents(filter_dict=filter,start=start,stop=stop)


async def update_agent_by_id(agent_id: str, agent_data: AgentUpdate) -> AgentOut:
    """updates an entry of agent in the database

    Raises:
        HTTPException 404(not found): if Agent not found or update failed
        HTTPException 400(not found): Invalid agent ID format

    Returns:
        _type_: AgentOut
    """
    if not ObjectId.is_valid(agent_id):
        raise HTTPException(status_code=400, detail="Invalid agent ID format")

    filter_dict = {"_id": ObjectId(agent_id)}
    result = await update_agent(filter_dict, agent_data)

    if not result:
        raise HTTPException(status_code=404, detail="Agent not found or update failed")

    return result



async def authenticate_agent(user_data:UserBase )->UserOut:
    user = await get_agent(filter_dict={"email":user_data.email})

    if user != None:
        if check_password(password=user_data.password,hashed=user.password ):
            user.password=""
            access_token = await add_access_tokens(token_data=accessTokenCreate(userId=user.id))
            refresh_token  = await add_refresh_tokens(token_data=refreshTokenCreate(userId=user.id,previousAccessToken=access_token.accesstoken))
            user.access_token= access_token.accesstoken 
            user.refresh_token = refresh_token.refreshtoken
            return user
        else:
            raise HTTPException(status_code=401, detail="Unathorized, Invalid Login credentials")
    else:
        raise HTTPException(status_code=404,detail="User not found")