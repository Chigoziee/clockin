from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from core.config import settings

client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None
admin_collection: AsyncIOMotorCollection = None
users_collection: AsyncIOMotorCollection = None

async def connect_to_mongo():
    global client, db, admin_collection, users_collection
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    admin_collection = db["admin"]
    users_collection = db["user"]

async def close_mongo_connection():
    client.close()
