from fastapi import FastAPI
from api.routes import admin, user
from contextlib import asynccontextmanager
from db.mongo import connect_to_mongo, close_mongo_connection
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(title="Employee Biometric Sign-in System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.admin_router)
app.include_router(user.user_router)

@app.get("/")
def home():
    return {"message": "Welcome to the Employee Sign-in System"}
