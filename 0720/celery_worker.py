# celery_worker.py
from celery import Celery
from main import call_knowledge_model_api  # 你的AI推理函数

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",  # Redis地址
    backend="redis://localhost:6379/0"
)

@celery_app.task
def ai_task(user_input):
    return call_knowledge_model_api(user_input)