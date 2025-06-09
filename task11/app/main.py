from fastapi import FastAPI
from .tasks import send_email

app = FastAPI()

@app.get("/send-email/{email}")
def trigger_email(email: str):
    send_email.delay(email)
    return {"message": "Email sending started"}
