from fastapi import FastAPI
from routes import admin, user


app = FastAPI(title="Employee Biometric Sign-in System")
app.include_router(admin.admin_router)
app.include_router(user.user_router)

@app.get("/")
def home():
    return {"message": "Welcome to the Employee Sign-in System"}
