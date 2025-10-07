# ============================================================================
#AGENT SCHEMA 
# ============================================================================
# This file was auto-generated on: 2025-09-24 23:30:00 WAT
# It contains Pydantic classes  database
# for managing attributes and validation of data in and out of the MongoDB database.
#
# ============================================================================

from schemas.imports import *
from pydantic import Field
import time

class AgentBase(BaseModel):
    email: EmailStr
    full_name:str
    phone_number: str
    certificate_url: List[str]
    video_url: str
    personality_url: str
    primary_area_of_expertise: Optional[Skills] = None
    years_of_experience: Optional[int] = None
    three_most_commonly_used_tools_or_platforms: Optional[List[str]] = None
    available_hours_agent_can_commit: Optional[AvailableHoursAgentCanCommit] = None
    time_zone: Optional[UTCOffsets] = None
    portfolio_link: Optional[str] = None
    is_agent_open_to_calls_and_video_meetings: Optional[bool] = None
    does_agent_have_working_computer: Optional[bool] = None
    does_agent_have_stable_internet: Optional[bool] = None
    is_agent_comfortable_with_time_tracking_tools: Optional[bool] = None
    
class AgentCreate(AgentBase):
    # Add other fields here 
    date_created: int = Field(default_factory=lambda: int(time.time()))
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class AgentUpdate(BaseModel):
    # Add other fields here 
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class AgentOut(AgentBase):
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