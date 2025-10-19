# ============================================================================
#LOGS SCHEMA 
# ============================================================================
# This file was auto-generated on: 2025-10-17 00:30:27 WAT
# It contains Pydantic classes  database
# for managing attributes and validation of data in and out of the MongoDB database.
#
# ============================================================================

from schemas.imports import *
from pydantic import Field
import time

class LogsBase(BaseModel):
    job_id: str
    
    log_comment: str
    files: List[str]
    hours: int
    log_title: str

class LogsCreate(LogsBase):
    # Add other fields here
    agent_id:str
    
    client_approved:bool=Field(default=False) 
    date_created: int = Field(default_factory=lambda: int(time.time()))
    last_updated: int = Field(default_factory=lambda: int(time.time()))
class LogReject(BaseModel):
    rejection_reason:str
class LogsUpdate(BaseModel):
    # Add other fields here
    client_approved:Optional[bool]=None
    rejection_reason:Optional[str]=None 
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class LogsOut(LogsBase):
    # Add other fields here
    agent_id:str
    client_approved:bool 
    id: Optional[str] =None
    date_created: Optional[int] = None
    last_updated: Optional[int] = None
    rejection_reason:Optional[str]=None 
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