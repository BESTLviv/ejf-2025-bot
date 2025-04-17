from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client["ejf-2025-bot"]

users_collection = db["users"]
cv_collection = db["cv"]

async def get_database():
    client = AsyncIOMotorClient(MONGO_URI)  
    db = client["ejf-2025-bot"]  
    return db

async def save_user_data(user_id: int, name: str, course: str, university: str, speciality: str):
    await users_collection.update_one(
        {"telegram_id": user_id},
        {"$set": {
            "name": name,
            "course": course,
            "university": university,
            "speciality": speciality,
            "registered": True
        }},
        upsert=True
    )

async def add_user(user_data: dict):
    existing = await users_collection.find_one({"telegram_id": user_data["telegram_id"]})
    if not existing:
        await users_collection.insert_one(user_data)

async def get_user(user_id: int):
    return await users_collection.find_one({"telegram_id": user_id})

async def add_cv(user_id: int, cv_text: str = None, cv_file_path: str = None):
    cv_data = {
        "user_id": user_id,
        "cv_text": cv_text,
        "cv_file_path": cv_file_path,
    }
    await cv_collection.insert_one(cv_data)

async def get_cv(user_id: int):
    return await cv_collection.find_one({"telegram_id": user_id})

async def count_users():
    return await users_collection.count_documents({"registered": True})

async def get_all_users():
    return users_collection.find({})
