# app/main.py
from fastapi import FastAPI
from routes import auth


app = FastAPI(title="Employee Biometric Sign-in System")
app.include_router(auth.user_router)


@app.get("/")
def home():
    return {"message": "Welcome to the Employee Sign-in System"}
