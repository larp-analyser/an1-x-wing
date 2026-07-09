import asyncio
import httpx
import dspy
import logging
from pydantic import BaseModel, Field
from typing import Dict, Any, Tuple
from .config import settings

logger = logging.getLogger(__name__)

# Configure DSPy with Groq LM for delay intuition
try:
    groq_lm = dspy.Groq(
        model='openai/gpt-oss-120b', 
        api_key=settings.groq_api_key,
        temperature=1,
        max_tokens=8192,
        top_p=1,
        reasoning_effort="medium"
    )
    dspy.settings.configure(lm=groq_lm)
except Exception as e:
    logger.warning(f"Could not configure Groq LM: {e}")

class DelayDecision(BaseModel):
    delay_minutes: int = Field(..., description="The calculated stealth delay in minutes")

class DelaySignature(dspy.Signature):
    """
    Calculate a stealth delay (in minutes) for posting a reply to a topic.
    The delay must be an integer. 
    Use shorter delays for fast-moving or critical topics, and longer delays for casual topics to simulate human behavior.
    """
    topic_text = dspy.InputField(desc="The text of the topic or tweet being replied to")
    generated_reply = dspy.InputField(desc="The generated reply from LARPAn1")
    decision: DelayDecision = dspy.OutputField(desc="The delay decision containing the integer delay_minutes")

async def get_larpan1_response(tweet_data: Dict[str, Any]) -> str:
    payload = {
        "message": tweet_data.get("text", ""),
        "sender_id": tweet_data.get("sender_id", "unknown"),
        "username": tweet_data.get("username", "unknown"),
        "display_name": tweet_data.get("display_name", "unknown"),
        "group_name": "twitter_public",
        "channel": "timeline",
        "platform": "twitter",
        "tagged_users": [],
        "force_reply": True,
        "mode": "auto"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.larpan1_url,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("reply")
        except Exception as e:
            logger.error(f"Failed to get LARPAn1 response: {e}")
            return None

def calculate_delay(topic_text: str, generated_reply: str) -> int:
    try:
        predictor = dspy.TypedPredictor(DelaySignature)
        result = predictor(topic_text=topic_text, generated_reply=generated_reply)
        delay = result.decision.delay_minutes
        
        return delay
    except Exception as e:
        logger.error(f"Delay calculation failed, defaulting to 15 min. Error: {e}")
        return 15

async def process_tweet(tweet_data: Dict[str, Any]) -> Tuple[str, int]:
    """
    Process the tweet: get LARPAn1 reply and calculate delay.
    Returns (reply_text, delay_minutes). If reply fails, returns (None, 0).
    """
    reply = await get_larpan1_response(tweet_data)
    if not reply:
        return None, 0
    
    # Calculate delay asynchronously to avoid blocking the loop
    delay = await asyncio.to_thread(calculate_delay, tweet_data.get("text", ""), reply)
    
    return reply, delay
