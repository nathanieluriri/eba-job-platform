# ============================================================================
#ALERTS SCHEMA 
# ============================================================================
# This file was auto-generated on: 2025-09-30 13:48:37 WAT
# It contains Pydantic classes  database
# for managing attributes and validation of data in and out of the MongoDB database.
#
# ============================================================================

from schemas.imports import *
from pydantic import Field
import time

class AlertsBase(BaseModel):
    # Add other fields here
    priority:
    alert_type:
    alert_title:
    alert_description:
    alert_primary_action:
    alert_secondary_action: 
    pass

class AlertsCreate(AlertsBase):
    # Add other fields here

    
    date_created: int = Field(default_factory=lambda: int(time.time()))
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class AlertsUpdate(BaseModel):
    # Add other fields here 
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class AlertsOut(AlertsBase):
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