# ============================================================================
#ALERTS SCHEMA 
# ============================================================================
# This file was auto-generated on: 2025-09-30 13:48:37 WAT
# It contains Pydantic classes  database
# for managing attributes and validation of data in and out of the MongoDB database.
#
# ============================================================================

from schemas.imports import *
from pydantic import Field,ConfigDict
import time
 
class AlertsBase(BaseModel):

    user_type: UserTypes = Field(..., description="The type of user receiving the alert (e.g., agent, client, admin).")
    user_id: str = Field(..., description="The unique identifier of the user receiving the alert.")
    priority: PriorityStatus = Field(..., description="The priority level of the alert (e.g., high, medium, low).")
    alert_type: AlertType = Field(..., description="The type/category of alert being sent.")
    alert_title: str = Field(..., description="A short, human-readable title for the alert.")
    alert_description: str = Field(..., description="A detailed explanation of the alert's purpose or context.")
    alert_primary_action: str = Field(..., description="Primary action the user should take in response to the alert.")
    alert_secondary_action: str = Field(..., description="Secondary (optional) action the user can take.")


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