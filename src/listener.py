import asyncio
import httpx
import feedparser
import logging
from typing import AsyncGenerator, Dict, Any
from .config import settings
from .db import is_processed

logger = logging.getLogger(__name__)

async def fetch_rss_feed(client: httpx.AsyncClient, instance: str, topic: str) -> str:
    url = f"{instance}/search/rss"
    params = {"q": topic}
    try:
        response = await client.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.warning(f"Failed to fetch from {instance} for topic '{topic}': {e}")
        return ""

async def get_new_tweets() -> AsyncGenerator[Dict[str, Any], None]:
    async with httpx.AsyncClient() as client:
        for topic in settings.topics_list:
            for instance in settings.instances_list:
                xml_content = await fetch_rss_feed(client, instance, topic)
                if not xml_content:
                    continue
                
                feed = feedparser.parse(xml_content)
                for entry in feed.entries:
                    text = getattr(entry, 'title', "")
                    
                    # Nitter ID typically looks like: https://nitter.net/user/status/123456789#m
                    # We can use the full ID or extract the numerical part. Let's use the guid/id.
                    tweet_id = getattr(entry, 'id', getattr(entry, 'link', str(hash(text))))
                    
                    if await is_processed(tweet_id):
                        continue
                    
                    # Author in Nitter RSS is usually '@username'
                    author = getattr(entry, 'author', "unknown")
                    username = author.lstrip('@')
                    
                    # In Nitter RSS, the link contains the platform status URL path
                    link = getattr(entry, 'link', "")
                    
                    # Extract raw sender_id if possible, or just use username as sender_id for bridge
                    sender_id = username 
                    
                    yield {
                        "id": tweet_id,
                        "text": text,
                        "username": username,
                        "display_name": username,
                        "sender_id": sender_id,
                        "link": link
                    }
                
                # Stop trying other instances for this topic if one succeeds
                break
