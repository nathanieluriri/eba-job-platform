from bson import ObjectId
from typing_extensions import Self
from pydantic import GetJsonSchemaHandler
from pydantic import BaseModel, EmailStr, Field,model_validator
from pydantic_core import core_schema
from datetime import datetime,timezone,timedelta
from typing import Optional,List,Any
from enum import Enum
import time

class UserRoleBody(BaseModel):
    name:str
    description:str
    
class UserRoles(Enum):
    client=UserRoleBody(name="client",description="This user creates Job Postings")
    agent= UserRoleBody(name="agent",description="This user accepts job postings")
    
    
class UserRolesBase(str,Enum):
    client="client"
    agent="agent"
    
    
class UserTypes(str,Enum):
    agent= "agent"
    client=  "client"
    admin= "admin"
    
class JobStatus(str,Enum):
    active="active"
    pending="pending"
    
class JobCatgeries(str,Enum):
    web_development="Web Devlopment"
    mobile_development="Mobile Development"
    ui_ux_design="UI/UX Design"
    content_writing="Content Writing"
    digital_marketing="Digital Marketing"
    data_analysis="Data Analysis"
    other="Other"
    
    
class JobTimeline(BaseModel):
    start_date:int
    deadline:int
    
    
class Skills(str,Enum):
    web_development="Web Devlopment"
    mobile_development="Mobile Development"
    ui_ux_design="UI/UX Design"
    content_writing="Content Writing"
    digital_marketing="Digital Marketing"
    data_analysis="Data Analysis"
    other="Other"
    
    
class PriceBreakDown(BaseModel):
    Charges:float
    Tax:float
    
    
    
class PriorityStatus(str,Enum):
    very_high="very_high"
    high="high"
    medium="medium"
    low="low"
    
class AlertType(str,Enum):
    new_agent="new_agent"
    agent_completion_update="agent_completion_update"
    
class AlertActions(str,Enum):
    primary="primary"
    secondary="secondary"


class ClientReasonForSignUp(str,Enum): 
    just_hire_me_someone= "Just hire me someone"
    need_assitance_with_hiring ="Need assistance with hiring, training, onboarding and management for first month"
    
class ClientNeedAgentWorkHoursToBe(str,Enum):
    full_time = "160"
    part_time="80"
    both ="both"
   
class AvailableHoursAgentCanCommit(int,Enum):
    full_time=160
    part_time=80 
    
    
class UTCOffsets(str, Enum):
    """
    A list of all unique standard time zone UTC offsets.
    The member name is identical to its string value (e.g., UTC_MINUS_12_00 = "UTC-12:00").
    """
    
    # Negative Offsets (Behind UTC)
    UTC_MINUS_12_00 = "UTC-12:00"
    UTC_MINUS_11_00 = "UTC-11:00"
    UTC_MINUS_10_00 = "UTC-10:00"
    UTC_MINUS_09_30 = "UTC-09:30"
    UTC_MINUS_09_00 = "UTC-09:00"
    UTC_MINUS_08_00 = "UTC-08:00"
    UTC_MINUS_07_00 = "UTC-07:00"
    UTC_MINUS_06_00 = "UTC-06:00"
    UTC_MINUS_05_00 = "UTC-05:00"
    UTC_MINUS_04_30 = "UTC-04:30"
    UTC_MINUS_04_00 = "UTC-04:00"
    UTC_MINUS_03_30 = "UTC-03:30"
    UTC_MINUS_03_00 = "UTC-03:00"
    UTC_MINUS_02_00 = "UTC-02:00"
    UTC_MINUS_01_00 = "UTC-01:00"
    
    # Zero Offset
    UTC_PLUS_00_00  = "UTC+00:00"
    
    # Positive Offsets (Ahead of UTC)
    UTC_PLUS_01_00  = "UTC+01:00"
    UTC_PLUS_02_00  = "UTC+02:00"
    UTC_PLUS_03_00  = "UTC+03:00"
    UTC_PLUS_03_30  = "UTC+03:30"
    UTC_PLUS_04_00  = "UTC+04:00"
    UTC_PLUS_04_30  = "UTC-04:30"
    UTC_PLUS_05_00  = "UTC+05:00"
    UTC_PLUS_05_30  = "UTC+05:30"
    UTC_PLUS_05_45  = "UTC+05:45"
    UTC_PLUS_06_00  = "UTC+06:00"
    UTC_PLUS_06_30  = "UTC+06:30"
    UTC_PLUS_07_00  = "UTC+07:00"
    UTC_PLUS_08_00  = "UTC+08:00"
    UTC_PLUS_08_45  = "UTC+08:45"
    UTC_PLUS_09_00  = "UTC+09:00"
    UTC_PLUS_09_30  = "UTC+09:30"
    UTC_PLUS_10_00  = "UTC+10:00"
    UTC_PLUS_10_30  = "UTC+10:30"
    UTC_PLUS_11_00  = "UTC+11:00"
    UTC_PLUS_11_30  = "UTC+11:30"
    UTC_PLUS_12_00  = "UTC+12:00"
    UTC_PLUS_12_45  = "UTC+12:45"
    UTC_PLUS_13_00  = "UTC+13:00"
    UTC_PLUS_14_00  = "UTC+14:00"    
    

class StandardTimeZones(Enum):
    """
    A list of all unique standard time zone UTC offsets.
    Values are stored as datetime.timedelta objects for arithmetic.
    """
    
    # Negative Offsets (Behind UTC)
    UTC_MINUS_12_00 = timedelta(hours=-12)  # AoE / International Date Line West
    UTC_MINUS_11_00 = timedelta(hours=-11)  # Samoa Standard Time
    UTC_MINUS_10_00 = timedelta(hours=-10)  # Hawaii Standard Time
    UTC_MINUS_09_30 = timedelta(hours=-9, minutes=-30) # Marquesas Islands
    UTC_MINUS_09_00 = timedelta(hours=-9)   # Alaska Standard Time
    UTC_MINUS_08_00 = timedelta(hours=-8)   # Pacific Standard Time
    UTC_MINUS_07_00 = timedelta(hours=-7)   # Mountain Standard Time
    UTC_MINUS_06_00 = timedelta(hours=-6)   # Central Standard Time
    UTC_MINUS_05_00 = timedelta(hours=-5)   # Eastern Standard Time
    UTC_MINUS_04_30 = timedelta(hours=-4, minutes=-30) # Venezuela
    UTC_MINUS_04_00 = timedelta(hours=-4)   # Atlantic Standard Time
    UTC_MINUS_03_30 = timedelta(hours=-3, minutes=-30) # Newfoundland Standard Time
    UTC_MINUS_03_00 = timedelta(hours=-3)   # Argentina / Brasilia Time
    UTC_MINUS_02_00 = timedelta(hours=-2)   # South Georgia / Mid-Atlantic
    UTC_MINUS_01_00 = timedelta(hours=-1)   # Azores / Cape Verde Time
    
    # Zero Offset
    UTC_PLUS_00_00  = timedelta(hours=0)    # Coordinated Universal Time (UTC) / GMT
    
    # Positive Offsets (Ahead of UTC)
    UTC_PLUS_01_00  = timedelta(hours=1)    # Central European Time / West Africa Time
    UTC_PLUS_02_00  = timedelta(hours=2)    # Eastern European Time / South Africa Standard Time
    UTC_PLUS_03_00  = timedelta(hours=3)    # Moscow / East Africa Time
    UTC_PLUS_03_30  = timedelta(hours=3, minutes=30) # Iran Standard Time
    UTC_PLUS_04_00  = timedelta(hours=4)    # Gulf Standard Time
    UTC_PLUS_04_30  = timedelta(hours=4, minutes=30) # Afghanistan Time
    UTC_PLUS_05_00  = timedelta(hours=5)    # Pakistan / Uzbekistan Time
    UTC_PLUS_05_30  = timedelta(hours=5, minutes=30) # India / Sri Lanka Time
    UTC_PLUS_05_45  = timedelta(hours=5, minutes=45) # Nepal Time
    UTC_PLUS_06_00  = timedelta(hours=6)    # Bangladesh / Vostok Time
    UTC_PLUS_06_30  = timedelta(hours=6, minutes=30) # Myanmar / Cocos Islands Time
    UTC_PLUS_07_00  = timedelta(hours=7)    # Indochina / Western Indonesia Time
    UTC_PLUS_08_00  = timedelta(hours=8)    # China / Australian Western Standard Time
    UTC_PLUS_08_45  = timedelta(hours=8, minutes=45) # Australian Central Western Standard Time (Unofficial)
    UTC_PLUS_09_00  = timedelta(hours=9)    # Japan / Korea Standard Time
    UTC_PLUS_09_30  = timedelta(hours=9, minutes=30) # Australian Central Standard Time
    UTC_PLUS_10_00  = timedelta(hours=10)   # Australian Eastern Standard Time
    UTC_PLUS_10_30  = timedelta(hours=10, minutes=30) # Lord Howe Island
    UTC_PLUS_11_00  = timedelta(hours=11)   # Solomon Islands Time
    UTC_PLUS_11_30  = timedelta(hours=11, minutes=30) # Norfolk Island Time
    UTC_PLUS_12_00  = timedelta(hours=12)   # Fiji / New Zealand Standard Time
    UTC_PLUS_12_45  = timedelta(hours=12, minutes=45) # Chatham Islands
    UTC_PLUS_13_00  = timedelta(hours=13)   # Phoenix Islands / Tonga Time
    UTC_PLUS_14_00  = timedelta(hours=14)   # Line Islands Time
    
    
class PasswordResetInStep1(BaseModel):
    email:EmailStr
    
class PasswordResetOutStep1(BaseModel):
    reset_token:str
    
    
class PasswordResetInStep2(BaseModel):
    reset_token:str
    otp:str
    new_password:str
