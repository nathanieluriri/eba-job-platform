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
from services.alerts_service import (
    update_alerts_by_id,
    add_alerts
)
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
        new_data = AlertsCreate(**alert.model_dump())
        await add_alerts(alerts_data=new_data)
        

    asyncio.run(_add_new_alert())