# ============================================================================
#SETTINGS SCHEMA 
# ============================================================================
# This file was auto-generated on: 2025-10-19 14:02:53 WAT
# It contains Pydantic classes  database
# for managing attributes and validation of data in and out of the MongoDB database.
#
# ============================================================================

from schemas.imports import *
from pydantic import Field
import time

class SettingsBase(BaseModel):
    email_notifications: bool = Field(default=True, description="Receive notifications via email")
    sms_notifications: bool = Field(default=False, description="Receive notifications via SMS")
    push_notifications: bool = Field(default=True, description="Receive notifications via push messages")
    in_app_notifications: bool = Field(default=True, description="Receive notifications inside the app")
    marketing_notifications: bool = Field(default=False, description="Receive marketing or promotional updates")

class SettingsCreate(SettingsBase):
    # Add other fields here 
    date_created: int = Field(default_factory=lambda: int(time.time()))
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class SettingsUpdate(BaseModel):
    # Add other fields here 
    email_notifications: Optional[bool] =None
    sms_notifications: Optional[bool] =None
    push_notifications: Optional[bool] =None
    in_app_notifications: Optional[bool] =None
    marketing_notifications: Optional[bool] =None
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class SettingsOut(SettingsBase):
    # Add other fields here 
    date_created: Optional[int] = None
    last_updated: Optional[int] = None
    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }