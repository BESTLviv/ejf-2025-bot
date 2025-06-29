from motor.motor_asyncio import AsyncIOMotorClient
from config import load_config

config = load_config()


client = AsyncIOMotorClient(config.mongo_uri)
db = client["ejf-2025-bot"]  

users_collection = db["users"]
cv_collection = db["cv"]

async def get_database():
    client = AsyncIOMotorClient(config.mongo_uri)
    db = client["ejf-2025-bot"]
    return db

async def save_user_data(user_id, user_name, name, course, university, speciality):
    user_data = {
        "telegram_id": user_id,
        "username": user_name,
        "name": name,
        "course": course,
        "university": university,
        "speciality": speciality
    }

    # Використовуйте upsert правильно
    await users_collection.update_one(
        {"telegram_id": user_id},  # Фільтр
        {"$set": user_data},       # Дані для оновлення
        upsert=True                # Додати документ, якщо він не існує
    )
async def add_user(user_data: dict):
    existing = await users_collection.find_one({"telegram_id": user_data["telegram_id"]})
    if not existing:
        await users_collection.insert_one(user_data)

async def get_user(user_id: int):
    return await users_collection.find_one({"telegram_id": user_id})

async def add_cv(user_id: int, cv_file_path: str = None, position: str = None, 
                 languages: list = None, education: str = None, experience: str = None, 
                 skills: list = None, about: str = None, contacts: dict = None):
    user = await users_collection.find_one({"telegram_id": user_id})
    cv_data = {
        "telegram_id": user_id,
        "user_name": user["name"] if user else str(user_id),
        "cv_file_path": cv_file_path,
        "position": position,
        "languages": languages,
        "education": education,
        "experience": experience,
        "skills": skills,
        "about": about,
        "contacts": contacts
    }
    await cv_collection.update_one(
        {"telegram_id": user_id},  
        {"$set": cv_data},        
        upsert=True               
    )

async def get_cv(user_id: int):
    return await cv_collection.find_one({"telegram_id": user_id})

async def count_users():
    return await users_collection.count_documents({"registered": True})

async def get_all_users():
    return users_collection.find({})
async def count_all_users():
    return await users_collection.count_documents({})


async def update_cv_file_path(user_id: int, file_id: str) -> bool:
    result = await cv_collection.update_one(
        {"telegram_id": str(user_id)},
        {"$set": {"cv_file_path": file_id}}
    )
    return result.matched_count > 0