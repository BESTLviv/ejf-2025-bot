# from motor.motor_asyncio import AsyncIOMotorClient
# from config import load_config

# config = load_config()


# client = AsyncIOMotorClient(config.mongo_uri)
# db = client["ejf-2025-bot"]  

# users_collection = db["users"]
# cv_collection = db["cv"]

# async def get_database():
#     client = AsyncIOMotorClient(config.mongo_uri)
#     db = client["ejf-2025-bot"]
#     return db

# async def save_user_data(user_id, user_name, name, course, university, speciality):
#     user_data = {
#         "telegram_id": user_id,
#         "username": user_name,
#         "name": name,
#         "course": course,
#         "university": university,
#         "speciality": speciality
#     }

#     # Використовуйте upsert правильно
#     await users_collection.update_one(
#         {"telegram_id": user_id},  # Фільтр
#         {"$set": user_data},       # Дані для оновлення
#         upsert=True                # Додати документ, якщо він не існує
#     )
# async def add_user(user_data: dict):
#     existing = await users_collection.find_one({"telegram_id": user_data["telegram_id"]})
#     if not existing:
#         await users_collection.insert_one(user_data)

# async def get_user(user_id: int):
#     return await users_collection.find_one({"telegram_id": user_id})

# async def add_cv(user_id: int, cv_file_path: str = None, position: str = None, 
#                  languages: list = None, education: str = None, experience: str = None, 
#                  skills: list = None, about: str = None, contacts: dict = None):
#     user = await users_collection.find_one({"telegram_id": user_id})
#     cv_data = {
#         "telegram_id": user_id,
#         "user_name": user["name"] if user else str(user_id),
#         "cv_file_path": cv_file_path,
#         "position": position,
#         "languages": languages,
#         "education": education,
#         "experience": experience,
#         "skills": skills,
#         "about": about,
#         "contacts": contacts
#     }
#     await cv_collection.update_one(
#         {"telegram_id": user_id},  
#         {"$set": cv_data},        
#         upsert=True               
#     )

# async def get_cv(user_id: int):
#     return await cv_collection.find_one({"telegram_id": user_id})

# async def count_users():
#     return await users_collection.count_documents({"registered": True})

# async def get_all_users():
#     return users_collection.find({})
# async def count_all_users():
#     return await users_collection.count_documents({})


# async def update_cv_file_path(user_id: int, file_id: str) -> bool:
#     result = await cv_collection.update_one(
#         {"telegram_id": str(user_id)},
#         {"$set": {"cv_file_path": file_id}}
#     )
#     return result.matched_count > 0

from motor.motor_asyncio import AsyncIOMotorClient
from config import load_config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = load_config()

try:
    client = AsyncIOMotorClient(config.mongo_uri)
    db = client["ejf-2025-bot"]
    # Verify connection
    client.server_info()  # Raises an exception if connection fails
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

users_collection = db["users"]
cv_collection = db["cv"]

async def get_database():
    try:
        client = AsyncIOMotorClient(config.mongo_uri)
        db = client["ejf-2025-bot"]
        await client.server_info()  # Verify connection
        logger.info("Database connection established")
        return db
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise

async def save_user_data(user_id, user_name, name, course, university, speciality):
    user_data = {
        "telegram_id": user_id,
        "username": user_name,
        "name": name,
        "course": course,
        "university": university,
        "speciality": speciality
    }
    try:
        await users_collection.update_one(
            {"telegram_id": user_id},
            {"$set": user_data},
            upsert=True
        )
        logger.info(f"Saved user data for telegram_id: {user_id}")
    except Exception as e:
        logger.error(f"Error saving user data for telegram_id {user_id}: {e}")

async def add_user(user_data: dict):
    try:
        existing = await users_collection.find_one({"telegram_id": user_data["telegram_id"]})
        if not existing:
            await users_collection.insert_one(user_data)
            logger.info(f"Added new user: {user_data['telegram_id']}")
    except Exception as e:
        logger.error(f"Error adding user {user_data.get('telegram_id')}: {e}")

async def get_user(user_id: int):
    try:
        user = await users_collection.find_one({"telegram_id": user_id})
        return user
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return None

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
    required_fields = ['position', 'languages', 'education', 'experience', 'skills', 'about', 'contacts']
    missing_fields = [field for field in required_fields if cv_data[field] is None]
    if missing_fields:
        logger.warning(f"CV for user {user_id} missing fields: {', '.join(missing_fields)}")
    
    try:
        await cv_collection.update_one(
            {"telegram_id": user_id},
            {"$set": cv_data},
            upsert=True
        )
        logger.info(f"Added/Updated CV for user {user_id}")
    except Exception as e:
        logger.error(f"Error adding/updating CV for user {user_id}: {e}")

async def get_cv(user_id: int):
    try:
        cv = await cv_collection.find_one({"telegram_id": user_id})
        return cv
    except Exception as e:
        logger.error(f"Error getting CV for user {user_id}: {e}")
        return None

async def count_users():
    try:
        count = await users_collection.count_documents({"registered": True})
        return count
    except Exception as e:
        logger.error(f"Error counting users: {e}")
        return 0

async def get_all_users():
    try:
        return users_collection.find({})
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []

async def count_all_users():
    try:
        count = await users_collection.count_documents({})
        return count
    except Exception as e:
        logger.error(f"Error counting all users: {e}")
        return 0

async def update_cv_file_path(user_id: int, file_id: str) -> bool:
    try:
        result = await cv_collection.update_one(
            {"telegram_id": str(user_id)},
            {"$set": {"cv_file_path": file_id}}
        )
        if result.matched_count > 0:
            logger.info(f"Updated file_id for CV of user {user_id}")
            return True
        else:
            logger.warning(f"No CV found to update file_id for user {user_id}")
            return False
    except Exception as e:
        logger.error(f"Error updating CV file_id for user {user_id}: {e}")
        return False