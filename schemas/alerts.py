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
    unread:bool = Field(default=True)
class AlertsUpdate(BaseModel):
    # Add other fields here 
    last_updated: int = Field(default_factory=lambda: int(time.time()))
    unread:bool = Field(default=False)

class AlertsOut(AlertsBase):
    # Add other fields here 
    id: Optional[str] =None
    date_created: Optional[int] = None
    last_updated: Optional[int] = None
    unread:Optional[bool] = Field(default=True)
    @model_validator(mode='before')
    def set_dynamic_values(cls,values):
        if isinstance(values,dict):
            if values.get('id',None)==None: 
                values['id']= str(values.get('_id'))
            return values
    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        
        
        
class ListOfAlertsOut(BaseModel):
    alerts:Optional[List[AlertsOut]]=[]
    total_number_of_unread:Optional[int]=0

alert_examples = {
    "admin_very_high_system_update": {
        "summary": "Admin: Very High System Update",
        "description": "A critical system update notification for an admin.",
        "value": {
            "user_type": "admin",
            "user_id": "admin-001",
            "priority": "very_high",
            "alert_type": "system_update",
            "alert_title": "Critical Patch Required",
            "alert_description": "System vulnerability (CVE-2025-1234) detected. Apply patch 1.A.3 immediately.",
            "alert_primary_action": "/admin/patches/1A3",
            "alert_secondary_action": "/admin/system/health"
        }
    },
    "client_high_payment_failed": {
        "summary": "Client: High Priority Payment",
        "description": "Alert a client that their monthly subscription payment has failed.",
        "value": {
            "user_type": "client",
            "user_id": "client-882",
            "priority": "high",
            "alert_type": "payment_failed",
            "alert_title": "Payment Failed",
            "alert_description": "Your payment for invoice #INV-9982 failed. Please update your billing information to maintain service.",
            "alert_primary_action": "/billing/update",
            "alert_secondary_action": "/billing/history"
        }
    },
    "agent_medium_new_task": {
        "summary": "Agent: Medium Priority Task",
        "description": "Assigning a new, standard-priority task to an agent.",
        "value": {
            "user_type": "agent",
            "user_id": "agent-451",
            "priority": "medium",
            "alert_type": "task_assigned",
            "alert_title": "New Task: Blog Post",
            "alert_description": "Client 'TechCorp' has assigned you a new task: 'Write 500-word blog post on AI trends'.",
            "alert_primary_action": "/tasks/task-721",
            "alert_secondary_action": "/clients/techcorp/details"
        }
    },
    "client_medium_new_message": {
        "summary": "Client: New Message",
        "description": "Notifying a client they have a new message from their agent.",
        "value": {
            "user_type": "client",
            "user_id": "client-777",
            "priority": "medium",
            "alert_type": "new_message",
            "alert_title": "New Message from Agent Bob",
            "alert_description": "You have a new message from your agent regarding the 'Project Phoenix' milestone.",
            "alert_primary_action": "/messages/thread-192",
            "alert_secondary_action": "/projects/phoenix"
        }
    },
    "agent_low_reminder": {
        "summary": "Agent: Low Priority Reminder",
        "description": "A low-priority reminder for an agent to update their profile.",
        "value": {
            "user_type": "agent",
            "user_id": "agent-303",
            "priority": "low",
            "alert_type": "account_warning",
            "alert_title": "Update Your Portfolio",
            "alert_description": "Your portfolio seems to be 6 months old. Consider updating it to attract new clients.",
            "alert_primary_action": "/profile/portfolio/edit",
            "alert_secondary_action": "/dismiss"
        }
    },
    "admin_high_security_alert": {
        "summary": "Admin: High Security Alert",
        "description": "Alerting an admin to a potential security breach on a user account.",
        "value": {
            "user_type": "admin",
            "user_id": "admin-002",
            "priority": "high",
            "alert_type": "account_warning",
            "alert_title": "Suspicious Login Detected",
            "alert_description": "User 'client-123' account had 5 failed login attempts from an unknown IP. Account has been temporarily locked.",
            "alert_primary_action": "/users/client-123/manage",
            "alert_secondary_action": "/security/logs/ip-123.45.67.89"
        }
    },
    "client_very_high_deadline": {
        "summary": "Client: Very High Deadline",
        "description": "An urgent, final reminder to a client about an approaching deadline for action.",
        "value": {
            "user_type": "client",
            "user_id": "client-500",
            "priority": "very_high",
            "alert_type": "project_deadline",
            "alert_title": "FINAL NOTICE: Project Approval Due",
            "alert_description": "Project 'E-commerce Launch' is scheduled to go live in 24 hours. Your final approval is required immediately to proceed.",
            "alert_primary_action": "/projects/ecommerce/approve",
            "alert_secondary_action": "/projects/ecommerce/contact-manager"
        }
    },
    "agent_high_urgent_message": {
        "summary": "Agent: Urgent Client Message",
        "description": "Forwarding a high-priority, time-sensitive message from a client to an agent.",
        "value": {
            "user_type": "agent",
            "user_id": "agent-765",
            "priority": "high",
            "alert_type": "new_message",
            "alert_title": "URGENT: Client 'BigCorp' Request",
            "alert_description": "Client 'BigCorp' has reported a critical issue with their live site. Please respond immediately.",
            "alert_primary_action": "/messages/thread-201",
            "alert_secondary_action": "/clients/bigcorp/call"
        }
    },
    "admin_low_weekly_report": {
        "summary": "Admin: Low Priority Report",
        "description": "A routine, low-priority notification that a weekly report is ready.",
        "value": {
            "user_type": "admin",
            "user_id": "admin-001",
            "priority": "low",
            "alert_type": "generic_notification",
            "alert_title": "Weekly Report Ready",
            "alert_description": "Your weekly user activity report (Oct 21-27) is generated and ready for review.",
            "alert_primary_action": "/reports/weekly/latest",
            "alert_secondary_action": "/reports/generate-custom"
        }
    },
    "client_low_payment_confirmation": {
        "summary": "Client: Payment Confirmation",
        "description": "A low-priority, informational alert confirming a payment was successful.",
        "value": {
            "user_type": "client",
            "user_id": "client-882",
            "priority": "low",
            "alert_type": "payment_received",
            "alert_title": "Payment Received!",
            "alert_description": "We successfully received your payment for invoice #INV-9982. Thank you!",
            "alert_primary_action": "/billing/invoice/INV-9982",
            "alert_secondary_action": "/billing/history"
        }
    },
    "agent_medium_deadline_reminder": {
        "summary": "Agent: Task Deadline Reminder",
        "description": "A standard reminder for an agent about an upcoming task deadline.",
        "value": {
            "user_type": "agent",
            "user_id": "agent-451",
            "priority": "medium",
            "alert_type": "project_deadline",
            "alert_title": "Task Deadline Tomorrow",
            "alert_description": "Your task 'Write 500-word blog post on AI trends' is due in 24 hours.",
            "alert_primary_action": "/tasks/task-721",
            "alert_secondary_action": "/tasks/task-721/request-extension"
        }
    }
}
