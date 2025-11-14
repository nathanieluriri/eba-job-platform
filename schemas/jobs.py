# ============================================================================
#JOBS SCHEMA 
# ============================================================================
# This file was auto-generated on: 2025-09-27 09:01:53 WAT
# It contains Pydantic classes  database
# for managing attributes and validation of data in and out of the MongoDB database.
#
# ============================================================================

from schemas.agent import AgentOut
from schemas.imports import *
from pydantic import Field

import time

class JobsBase(BaseModel):
    # Add other fields here
    project_title:str
    primary_area_of_expertise: JobCatgeries
    budget:int
    description:str 
    timeline:JobTimeline
 
 
class JobMeeting(BaseModel):
    job_id:str
    agent_id:str
    meeting_time:int
 
class JobsCreate(JobsBase):
    # Add other fields here
    recommended_agents:Optional[List[AgentOut]]=None
    client_id:str
    admin_approved:bool = Field(default=False)
    isCompleted:Optional[bool]=Field(default=False)
    break_down:PriceBreakDown= Field(default=PriceBreakDown(Service=0,Charges=0,Tax=0))
    status: JobStatus = Field(default=JobStatus.pending)
    date_created: int = Field(default_factory=lambda: int(time.time()))
    last_updated: int = Field(default_factory=lambda: int(time.time()))
    @model_validator(mode='after')
    def set_dynamic_values(self)-> Self:
        self.break_down=PriceBreakDown(Charges=5,Tax=5)
        return self
    
class JobsProposal(BaseModel):
    proposal:str
    agent:AgentOut
    break_down:Optional[PriceBreakDown]=None 
    timeline:Optional[JobTimeline]=None
    
class JobsUpdate(BaseModel):
    # Add other fields here
 
    timeline:Optional[JobTimeline]=None
    description:Optional[str]=None
    requirement:Optional[str]=None
     
    selected_agents:Optional[List[AgentOut]]=None
    primary_area_of_expertise: Optional[JobCatgeries]=None
    admin_approved:Optional[bool] =None
    client_approved:Optional[bool] =None
    client_rejection_reason:Optional[str]=None
    rejection_reason:Optional[str]=None
    break_down:Optional[PriceBreakDown]=None 
    status:Optional[JobStatus]=None 
    isCompleted:Optional[bool]=None
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class JobsOut(JobsBase):
    # Add other fields here 
    client_id:str
    id: Optional[str] =None
    date_created: Optional[int] = None
    last_updated: Optional[int] = None
    client_approved:Optional[bool] =False
    proposal:Optional[str]=None
    recommended_agents:Optional[List[AgentOut]]=None
    selected_agents:Optional[List[AgentOut]]=None
    client_rejection_reason:Optional[str]=None
    rejection_reason:Optional[str]=None
    isCompleted:Optional[bool]=Field(default=False)
    admin_approved:bool = Field(default=False)
    break_down:PriceBreakDown= Field(default=PriceBreakDown(Service=0,Charges=0,Tax=0))
    status: JobStatus = Field(default=JobStatus.pending)
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