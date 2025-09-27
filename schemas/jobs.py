# ============================================================================
#JOBS SCHEMA 
# ============================================================================
# This file was auto-generated on: 2025-09-27 09:01:53 WAT
# It contains Pydantic classes  database
# for managing attributes and validation of data in and out of the MongoDB database.
#
# ============================================================================

from schemas.imports import *
from pydantic import Field
import time

class JobsBase(BaseModel):
    # Add other fields here
    project_title:str
    category: JobCatgeries
    budget:int
    description:str
    requirement:str
    skills_needed:Skills
    timeline:JobTimeline
    pass

class JobsCreate(JobsBase):
    # Add other fields here
    client_id:str
    status: JobStatus = Field(default=JobStatus.pending)
    date_created: int = Field(default_factory=lambda: int(time.time()))
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class JobsUpdate(BaseModel):
    # Add other fields here
    skills_needed:Optional[Skills]=None
    timeline:Optional[JobTimeline]=None
    description:Optional[str]=None
    requirement:Optional[str]=None
    skills_needed:Optional[Skills]=None
    category: Optional[JobCatgeries]=None
    budget:Optional[int]=None
    status:Optional[JobStatus]=None 
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class JobsOut(JobsBase):
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