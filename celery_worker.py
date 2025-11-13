import os
from celery import Celery
from dotenv import load_dotenv
import asyncio
import celery_aio_pool as aio_pool
from schemas.alerts import (
AlertsBase,
AlertsUpdate,
List,
AlertsCreate,
AlertsOut,
)
from schemas.imports import AlertType, UserTypes,PriorityStatus
from schemas.jobs import JobsBase, JobsCreate
from services.admin_service import retrieve_admins
from services.agent_service import retrieve_agents
from services.alerts_service import (
    update_alerts_by_id,
    add_alerts
)
from services.jobs_service import add_jobs
load_dotenv()

broker_url = os.getenv("CELERY_BROKER_URL")
backend_url = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery("worker", broker=broker_url, backend=backend_url,)
celery_app.conf.update(task_track_started=True)

@celery_app.task(name="celery_worker.test_scheduler")
def test_scheduler(message):
    print(message)
    

@celery_app.task(name="celery_worker.update_unread_alerts")
async def update_unread_alerts(alerts: list[dict]):
    tasks = []
    for alert in alerts:
        update_data = AlertsUpdate()
        alert_obj = AlertsOut(**alert)
        tasks.append(update_alerts_by_id(alerts_id=alert_obj.id, alerts_data=update_data))

    # Run all async tasks concurrently
    await asyncio.gather(*tasks)
    return "done"
    
@celery_app.task(name="celery_worker.add_new_alert")
def add_new_alert(alert: AlertsBase):
    async def _add_new_alert():
        new_data = AlertsCreate(**alert)
        if new_data.user_type == UserTypes.admin:
            list_of_admins =await retrieve_admins(start=0,stop=100)
            for admin in list_of_admins:
                new_data.user_id = admin.id
                await add_alerts(alerts_data=new_data)     
        if new_data.user_type != UserTypes.admin:   
            await add_alerts(alerts_data=new_data)
        

    asyncio.run(_add_new_alert())
    
    
    
    
@celery_app.task(name="celery_worker.add_new_job")
async def add_new_job(job:JobsBase):    
    new_data = JobsCreate(**job)
    filter_dict = {"primary_area_of_expertise":new_data.primary_area_of_expertise}
    agents = await retrieve_agents(start=0, stop=100,filter=filter_dict)
    new_data.recommended_agents=agents
    new_job = await add_jobs(jobs_data=new_data)
    alert_client = AlertsCreate(user_type=UserTypes.client,user_id=new_data.client_id,priority=PriorityStatus.medium,alert_type=AlertType.generic_notification,alert_title="New Job Created Successfully",alert_description=f"You Just created a new job titled: {new_job.project_title}",alert_primary_action="Set meetings ",alert_secondary_action="Cancel",)
    await add_alerts(alerts_data=alert_client)
    for agent in agents:
        alert_agent = AlertsCreate(user_type=UserTypes.agent,user_id=agent.id,priority=PriorityStatus.medium,alert_type=AlertType.generic_notification,alert_title="New Job Posted and you were recommended",alert_description=f"You Just got recommended for a new job titled: {new_job.project_title}",alert_primary_action="Mark as read ",alert_secondary_action="Ignore",)
        await add_alerts(alerts_data=alert_agent)
    list_of_admins =await retrieve_admins(start=0,stop=100)
    for admin in list_of_admins:
        alert_admin = AlertsCreate(user_type=UserTypes.admin,user_id=admin.id,priority=PriorityStatus.medium,alert_type=AlertType.generic_notification,alert_title="New Job Created Successfully",alert_description=f"Client Just created a new job titled: {new_job.project_title}",alert_primary_action="Mark as read",alert_secondary_action="Cancel",)
        
        await add_alerts(alerts_data=alert_admin)
    
 
    