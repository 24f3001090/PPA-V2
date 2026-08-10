from app import app
from celery import Celery, Task
from celery.schedules import crontab

celery_app = Celery('tasks', broker='redis://localhost:6379/1', backend='redis://localhost:6379/2', include=['tasks'])

class FlaskTask(Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery_app.Task = FlaskTask
celery_app.conf.timezone = 'Asia/Kolkata'

celery_app.conf.beat_schedule = {
    'monthly-placement-report': {
        'task': 'tasks.send_report',
        'schedule': crontab(hour=18, minute=20),
    },
    'daily-interview-reminder': {
        'task': 'tasks.send_int_reminder',
        'schedule': crontab(hour=18, minute=20),
    },
}