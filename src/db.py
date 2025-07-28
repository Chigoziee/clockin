from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("MONGO_DB_NAME")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

admin_collection = db["admin"]
users_collection = db["user"]


# import asyncio

# async def find_user():
#     users = await users_collection.find({"organization": "Clockin"}).to_list()
#     if users:
#         users = [{i:v for i, v in user.items() if i in ["firstName", "lastName", "email", "designation", "image_url"]} for user in users]
#         print(users[0])
#     else:
#         print("User not found")

# asyncio.run(find_user())