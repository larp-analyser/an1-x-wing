import motor.motor_asyncio
import pymongo
import logging
from datetime import datetime, timezone
from .config import settings

logger = logging.getLogger(__name__)

client = None
db = None
collection = None

async def init_db():
    global client, db, collection
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)
        db = client["larpan1_bridge"]
        collection = db["processed_tweets"]
        
        # Ensure a unique index on tweet_id
        await collection.create_index("tweet_id", unique=True)
        logger.info("MongoDB initialized and index created.")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        raise e

async def is_processed(tweet_id: str) -> bool:
    if collection is None:
        return False
    doc = await collection.find_one({"tweet_id": tweet_id})
    return doc is not None

async def mark_processed(tweet_id: str):
    if collection is None:
        return
    try:
        await collection.insert_one({
            "tweet_id": tweet_id,
            "processed_at": datetime.now(timezone.utc)
        })
    except pymongo.errors.DuplicateKeyError:
        pass  # Already processed
    except Exception as e:
        logger.error(f"Failed to mark tweet {tweet_id} as processed: {e}")
