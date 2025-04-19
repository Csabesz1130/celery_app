import random
import logging
from celery import Celery
from celery.schedules import crontab
from datetime import datetime
from .models import db, TaskResult
from flask import Flask

app = Celery('celery_app')
app.config_from_object('celery_app.celeryconfig')
logger = logging.getLogger(__name__)

# Flask alkalmazás létrehozása a Celery worker számára
flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(flask_app)

def save_task_result(task_name, status, result=None, error_message=None):
    with flask_app.app_context():
        try:
            task_result = TaskResult(
                task_name=task_name,
                status=status,
                result=str(result) if result else None,
                error_message=str(error_message) if error_message else None
            )
            db.session.add(task_result)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error saving task result: {str(e)}")
            db.session.rollback()

@app.task(bind=True)
def task_a(self):
    try:
        if random.choice([True, False]):
            result = 'Success A'
            logger.info('Task A succeeded')
            save_task_result('task_a', 'success', result)
            return result
        else:
            error = 'Random failure in Task A'
            logger.error('Task A failed')
            save_task_result('task_a', 'failure', error_message=error)
            raise Exception(error)
    except Exception as e:
        logger.error(f"Task A error: {str(e)}")
        raise

@app.task(bind=True)
def task_b(self):
    try:
        if random.random() < 0.3:
            error = 'Random failure in Task B'
            logger.error('Task B failed')
            save_task_result('task_b', 'failure', error_message=error)
            raise Exception(error)
        result = 'Success B'
        logger.info('Task B succeeded')
        save_task_result('task_b', 'success', result)
        return result
    except Exception as e:
        logger.error(f"Task B error: {str(e)}")
        raise

@app.task(bind=True)
def task_c(self):
    try:
        if random.random() < 0.2:
            error = 'Random failure in Task C'
            logger.error('Task C failed')
            save_task_result('task_c', 'failure', error_message=error)
            raise Exception(error)
        result = 'Success C'
        logger.info('Task C succeeded')
        save_task_result('task_c', 'success', result)
        return result
    except Exception as e:
        logger.error(f"Task C error: {str(e)}")
        raise

app.conf.beat_schedule = {
    'run-task-a': {
        'task': 'celery_app.tasks.task_a',
        'schedule': crontab(minute='*/1'),  # every 1 minute
    },
    'run-task-b': {
        'task': 'celery_app.tasks.task_b',
        'schedule': crontab(minute='*/2'),  # every 2 minutes
    },
    'run-task-c': {
        'task': 'celery_app.tasks.task_c',
        'schedule': crontab(minute='*/3'),  # every 3 minutes
    },
}
