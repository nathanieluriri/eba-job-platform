# ============================================================================
#APPLICATIONS SCHEMA 
# ============================================================================
# This file was auto-generated on: 2025-10-08 23:21:10 WAT
# It contains Pydantic classes  database
# for managing attributes and validation of data in and out of the MongoDB database.
#
# ============================================================================

from schemas.imports import *
from pydantic import Field
import time

class ApplicationsBase(BaseModel):
    # Add other fields here 
    job_id:str
    proposal:str
    
    

class ApplicationsCreate(ApplicationsBase):
    # Add other fields here 
    proposal_status:ProposalState
    agent_id:str
    date_created: int = Field(default_factory=lambda: int(time.time()))
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class ApplicationsUpdate(BaseModel):
    # Add other fields here 
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class ApplicationsOut(ApplicationsBase):
    # Add other fields here 
    id: Optional[str] =None
    proposal_status:ProposalState
    agent_id:str
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