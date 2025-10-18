
import asyncio
import os


from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_jobstore("mongodb", collection="background_jobs")
# EXAMPLE CODE FOR ADDING JOB
# scheduler.add_job(alarm, "date", run_date=alarm_time, args=[datetime.now()])
# alarm is a function, "date" is the trigger and run_date is the time for the trigger to happen
   