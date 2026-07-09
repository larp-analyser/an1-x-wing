import asyncio
import httpx
import logging
from .config import settings

logger = logging.getLogger(__name__)

from urllib.parse import urlparse

async def stealth_post_worker(tweet_link: str, reply: str, delay_minutes: int):
    """
    Sleeps for the calculated stealth delay, then posts the Quote Tweet via IFTTT.
    """
    logger.info(f"Stealth Worker: Sleeping for {delay_minutes} minutes before posting.")
    await asyncio.sleep(delay_minutes * 60)
    
    url = f"https://maker.ifttt.com/trigger/{settings.ifttt_event_name}/json/with/key/{settings.ifttt_webhook_key}"
    
    # Convert Nitter link to official x.com link to trigger the Quote Tweet embed
    parsed_url = urlparse(tweet_link)
    clean_path = parsed_url.path.replace("#m", "")
    x_link = f"https://x.com{clean_path}"
    
    # Appending the x.com link to the text forces X to render an embedded Quote Tweet
    formatted_reply = f"{reply}\n\n{x_link}"
    payload = {"value1": formatted_reply}
    
    logger.info(f"Stealth Worker: Waking up and posting to IFTTT...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=20.0)
            response.raise_for_status()
            logger.info("Stealth Worker: Successfully posted reply via IFTTT.")
        except Exception as e:
            logger.error(f"Stealth Worker: Failed to post via IFTTT: {e}")
