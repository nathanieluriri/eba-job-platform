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
from pydantic import Field, ConfigDict

import time

class JobsBase(BaseModel):
    # Add other fields here
    project_title:str
    primary_area_of_expertise: JobCatgeries
    description:str 
    timeline:JobTimeline
    model_config = ConfigDict(extra="forbid")
 
 
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
    break_down:PriceBreakDown= Field(default=PriceBreakDown(Charges=0,Tax=0))
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
    model_config = ConfigDict(extra="forbid")

class AdminJobProposal(BaseModel):
    proposal: str
    agent_id: Optional[str] = None
    agent: Optional[AgentOut] = None
    break_down: Optional[PriceBreakDown] = None
    timeline: Optional[JobTimeline] = None
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_agent_input(self) -> Self:
        if not self.agent_id and not self.agent:
            raise ValueError("agent_id or agent is required")
        return self
    
class JobsUpdate(BaseModel):
    # Add other fields here
    agent:Optional[AgentOut]=None
    timeline:Optional[JobTimeline]=None
    description:Optional[str]=None
    requirement:Optional[str]=None
    proposal:Optional[str]=None
    selected_agents:Optional[List[AgentOut]]=None
    primary_area_of_expertise: Optional[JobCatgeries]=None
    admin_approved:Optional[bool] =None
    client_approved:Optional[bool] =None
    client_rejection_reason:Optional[str]=None
    rejection_reason:Optional[str]=None
    break_down:Optional[PriceBreakDown]=None 
    status:Optional[JobStatus]=None 
    isCompleted:Optional[bool]=None
    proposal_created_by_user_id: Optional[str] = None
    proposal_created_by_role: Optional[str] = None
    proposal_created_via: Optional[str] = None
    proposal_agent_id: Optional[str] = None
    latest_proposal_id: Optional[str] = None
    last_updated: int = Field(default_factory=lambda: int(time.time()))
    model_config = ConfigDict(extra="forbid")

class JobsOut(JobsBase):
    # Add other fields here 
    client_id:str
    id: Optional[str] =None
    date_created: Optional[int] = None
    last_updated: Optional[int] = None
    client_approved:Optional[bool] =False
    proposal:Optional[str]=None
    recommended_agents:Optional[List[AgentOut]]=None
    selected_agents:Optional[List[AgentOut]]=[]
    client_rejection_reason:Optional[str]=None
    rejection_reason:Optional[str]=None
    isCompleted:Optional[bool]=Field(default=False)
    admin_approved:bool = Field(default=False)
    break_down:PriceBreakDown= Field(default=PriceBreakDown(Charges=0,Tax=0))
    status: JobStatus = Field(default=JobStatus.pending)
    proposal_created_by_user_id: Optional[str] = None
    proposal_created_by_role: Optional[str] = None
    proposal_created_via: Optional[str] = None
    proposal_agent_id: Optional[str] = None
    latest_proposal_id: Optional[str] = None
    @model_validator(mode='before')
    def set_dynamic_values(cls,values): # type: ignore
        values['id']= str(values.get('_id')) # type: ignore
        return values # type: ignore
    model_config = ConfigDict(
        extra="ignore",
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
