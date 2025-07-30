from motor.motor_asyncio import AsyncIOMotorClient
import os
from core.config import settings


MONGO_URI = settings.MONGO_URI
DATABASE_NAME = settings.MONGO_DB_NAME

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

admin_collection = db["admin"]
users_collection = db["user"]