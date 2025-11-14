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
    password: str | bytes
    full_name:str
    phone_number: str
    certificate_url: List[str]
    video_url: str
    personality_url: str
    primary_area_of_expertise:JobCatgeries
    years_of_experience: int 
    three_most_commonly_used_tools_or_platforms: List[str] 
    available_hours_agent_can_commit: AvailableHoursAgentCanCommit
    time_zone: UTCOffsets 
    portfolio_link: str 
    is_agent_open_to_calls_and_video_meetings: bool 
    does_agent_have_working_computer: bool 
    does_agent_have_stable_internet: bool 
    is_agent_comfortable_with_time_tracking_tools: bool 
    
class AgentCreate(AgentBase):
    # Add other fields here 
    date_created: int = Field(default_factory=lambda: int(time.time()))
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class AgentUpdate(BaseModel):
    # Add other fields here 
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class AgentOut(AgentBase):
    id:Optional[ObjectId] = Field(default=None, alias="_id")
    date_created: Optional[int] = None
    last_updated: Optional[int] = None

    # 👉 Include MongoDB fields if needed
     

    @model_validator(mode="before")
    @classmethod
    def populate_id(cls, values):
        """
        Convert MongoDB _id to string id before validation.
        """
        mongo_id = values.get("_id")
        if mongo_id:
            values["id"] = str(mongo_id)
        return values

    class Config:
        # allow aliasing like _id → id
        populate_by_name = True
        arbitrary_types_allowed = True
        
        # Convert ObjectId to string when serializing
        json_encoders = {
            ObjectId: lambda v: str(v)
        }