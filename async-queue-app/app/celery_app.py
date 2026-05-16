# Celery + Redis Config

from celery import Celery

# redis is our broker here (holds the task queue) and Our backend (stores results)

celery = Celery(
        "async_queue_app",
        broker = "redis://redis:6379/0",
        backend = "redis://redis:6379/0",
)

celery.conf.update(
    # Acknowledge task ONLY after it finishes (not when picked up)
    # This means if the worker crashes mid-task, the message goes back to the queue
    task_acks_late=True,
 
    # If a worker dies unexpectedly, re-queue its in-flight tasks
    task_reject_on_worker_lost=True,
 
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
 
    # How long to keep results in Redis (1 hour)
    result_expires=3600,
 
    # Timezone
    timezone="UTC",
    enable_utc=True,
)

# this is usally the core production setup when it comes to 
# using celery in a project, but here are some common additions :
# Task retries : retries tasks if it fails this is importatn for network/API/database failures
# Task_time_limit = 300 : prevent stuck tasks from running forever
# worker concurrency : Controls how many tasks run at once.
# More workers = more parallel processing.
# Separate queues : separate queue per app/service
# Monitoring : Flower,logging systems




















