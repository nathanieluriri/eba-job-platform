# ============================================================================
# CLIENT SERVICE
# ============================================================================
# This file was auto-generated on: 2025-09-24 23:31:18 WAT
# It contains  asynchrounous functions that make use of the repo functions 
# 
# ============================================================================

from bson import ObjectId
from fastapi import HTTPException
from typing import List

from repositories.client import (
    create_client,
    get_client,
    get_clients,
    update_client,
    delete_client,
)
from repositories.tokens_repo import (
    add_access_tokens,
    add_refresh_tokens,
    
)
from schemas.client import ClientCreate, ClientUpdate, ClientOut
from schemas.user_schema import UserBase,UserOut
from schemas.tokens_schema import accessTokenCreate,refreshTokenCreate
from security.hash import check_password

async def add_client(client_data: ClientCreate) -> ClientOut:
    """adds an entry of ClientCreate to the database and returns an object

    Returns:
        _type_: ClientOut
    """
    return await create_client(client_data)


async def remove_client(client_id: str):
    """deletes a field from the database and removes ClientCreateobject 

    Raises:
        HTTPException 400: Invalid client ID format
        HTTPException 404:  Client not found
    """
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail="Invalid client ID format")

    filter_dict = {"_id": ObjectId(client_id)}
    result = await delete_client(filter_dict)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Client not found")


async def retrieve_client_by_client_id(id: str) -> ClientOut:
    """Retrieves client object based specific Id 

    Raises:
        HTTPException 404(not found): if  Client not found in the db
        HTTPException 400(bad request): if  Invalid client ID format

    Returns:
        _type_: ClientOut
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid client ID format")

    filter_dict = {"_id": ObjectId(id)}
    result = await get_client(filter_dict)

    if not result:
        raise HTTPException(status_code=404, detail="Client not found")

    return result


async def retrieve_clients(filter=None,start=0,stop=100) -> List[ClientOut]:
    """Retrieves ClientOut Objects in a list

    Returns:
        _type_: ClientOut
    """
    return await get_clients(filter_dict=filter,start=start,stop=stop)


async def update_client_by_id(client_id: str, client_data: ClientUpdate) -> ClientOut:
    """updates an entry of client in the database

    Raises:
        HTTPException 404(not found): if Client not found or update failed
        HTTPException 400(not found): Invalid client ID format

    Returns:
        _type_: ClientOut
    """
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail="Invalid client ID format")

    filter_dict = {"_id": ObjectId(client_id)}
    result = await update_client(filter_dict, client_data)

    if not result:
        raise HTTPException(status_code=404, detail="Client not found or update failed")

    return result



async def authenticate_client(user_data:UserBase )->UserOut:
    user = await get_client(filter_dict={"email":user_data.email})

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