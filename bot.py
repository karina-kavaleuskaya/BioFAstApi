from fastapi import FastAPI, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from models import User, Container
from async_db import get_db
from celery import Celery
import telegram
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

BOT_TOKEN = '***********'
RESULTS_DIR = 'static/containers/{container_id}'

app = FastAPI()

# Celery setup
celery_app = Celery('bot', broker='amqp://guest:guest@localhost:5672//')


@celery_app.task
def send_analysis_results(container_id, chat_id):
    bot = telegram.Bot(token=BOT_TOKEN)
    results_dir = RESULTS_DIR.format(container_id=container_id)
    if os.path.exists(results_dir) and os.listdir(results_dir):
        for filename in os.listdir(results_dir):
            if filename.endswith('.txt'):
                results_file = os.path.join(results_dir, filename)
                if os.path.getsize(results_file) > 0:
                    with open(results_file, 'r') as file:
                        for line in file:
                            bot.send_message(chat_id=chat_id, text=line.strip())
                    print(f"Sent results for container {container_id} at {datetime.now()}")
                else:
                    print(f"Skipped empty file for container {container_id} at {datetime.now()}")
    else:
        bot.send_message(chat_id=chat_id, text="Извините, результаты анализа пока недоступны.")


@celery_app.task
async def send_results(container_id: int, db: Session = Depends(get_db)):
    try:
        container = db.query(Container).filter(Container.id == container_id).first()
        if container:
            user = container.user
            send_analysis_results.apply_async((container_id, user.telegram))
            return {"message": "Результаты анализа отправлены пользователю."}
        else:
            return {"error": "Контейнер не найден."}
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        return {"error": "Ошибка при отправке результатов."}


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.conf.beat_schedule = {
        'send_results': {
            'task': 'send_results',
            'schedule': 30.0,  # 5 minutes
        },
    }


