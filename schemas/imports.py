from bson import ObjectId
from typing_extensions import Self
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
    
    
class JobStatus(str,Enum):
    active="active"
    pending="pending"
    
class JobCatgeries(str,Enum):
    web_development="Web Devlopment"
    mobile_development="Mobile Development"
    ui_ux_design="UI/UX Design"
    content_writing="Content Writing"
    digital_marketing="Digital Marketing"
    data_analysis="Data Analysis"
    other="Other"
    
    
class JobTimeline(BaseModel):
    start_date:int
    deadline:int
    
    
class Skills(str,Enum):
    web_development="Web Devlopment"
    mobile_development="Mobile Development"
    ui_ux_design="UI/UX Design"
    content_writing="Content Writing"
    digital_marketing="Digital Marketing"
    data_analysis="Data Analysis"
    other="Other"
    
    
class PriceBreakDown(BaseModel):
    Service:int
    Charges:float
    Tax:float