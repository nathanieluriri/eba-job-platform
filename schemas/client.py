# ============================================================================
#CLIENT SCHEMA 
# ============================================================================
# This file was auto-generated on: 2025-09-24 23:29:54 WAT
# It contains Pydantic classes  database
# for managing attributes and validation of data in and out of the MongoDB database.
#
# ============================================================================

from schemas.imports import *
from pydantic import Field
import time

class ClientBase(BaseModel):
    email: EmailStr
    phone_number: str
    certificate_url: List[str]
    video_url: str
    personality_url: str
    company_name: Optional[str] = None
    company_email: Optional[str] = None
    company_address: Optional[str] = None
    full_name: Optional[str] = None
    services: Optional[List[Skills]] = None
    client_reason_for_signing_up: Optional[ClientReasonForSignUp] = None
    client_need_agent_work_hours_to_be: Optional[ClientNeedAgentWorkHoursToBe] = None



class ClientCreate(ClientBase):
    # Add other fields here 
    date_created: int = Field(default_factory=lambda: int(time.time()))
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class ClientUpdate(BaseModel):
    # Add other fields here 
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class ClientOut(ClientBase):
    # Add other fields here 
    id: Optional[str] =None
    date_created: Optional[int] = None
    last_updated: Optional[int] = None
    
    @model_validator(mode='before')
    def set_dynamic_values(cls,values):
        values['id']= str(values.get('_id'))
        return values
    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }