from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic import BaseModel, EmailStr, Field,model_validator
from pydantic_core import core_schema
from datetime import datetime,timezone
from typing import Optional,List,Any
from enum import Enum
import time

class UserRoleBody(BaseModel):
    name:str
    description:str
    
class UserRoles(Enum):
    client=UserRoleBody(name="client",description="This user creates Job Postings")
    agent= UserRoleBody(name="agent",description="This user accepts job postings")
    
    
class UserRolesBase(str,Enum):
    client="client"
    agent="agent"