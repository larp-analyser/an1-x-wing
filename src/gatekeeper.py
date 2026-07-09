import httpx
import logging
import json
from .config import settings

logger = logging.getLogger(__name__)

async def should_engage(tweet_text: str) -> bool:
    """
    Evaluates whether the bridge should engage with a tweet using NVIDIA's Mistral model.
    """
    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.nvidia_api_key}",
        "Accept": "application/json"
    }
    
    system_prompt = (
        "You are an AI gatekeeper for an automated response agent. "
        "Analyze the following post and determine if it is worth engaging with. "
        "A post is worth engaging with ONLY if it is: popular, controversial, scammy, inauthentic, or sensitive. "
        "You must respond in strict JSON format like this: {\"engage\": true, \"reason\": \"<your reason>\"}"
    )

    payload = {
        "model": "mistralai/mistral-large-3-675b-instruct-2512",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": tweet_text}
        ],
        "max_tokens": 1024,
        "temperature": 0.15,
        "top_p": 1.00,
        "response_format": {"type": "json_object"}
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(invoke_url, headers=headers, json=payload, timeout=20.0)
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            result = json.loads(content)
            
            engage = result.get("engage", False)
            reason = result.get("reason", "No reason provided")
            logger.info(f"Gatekeeper Decision: {engage} | Reason: {reason}")
            
            return engage
        except json.JSONDecodeError as e:
            logger.error(f"Gatekeeper failed to parse JSON: {e} | Content: {content}")
            return False
        except Exception as e:
            logger.error(f"Gatekeeper API call failed, defaulting to False. Error: {e}")
            return False
