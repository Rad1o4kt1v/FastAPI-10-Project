from time import sleep
from .celery_worker import celery

@celery.task
def send_email(to_email: str):
    print(f"Start sending email to {to_email}")
    sleep(5)
    print(f"Email sent to {to_email}")
    return f"Sent to {to_email}"
