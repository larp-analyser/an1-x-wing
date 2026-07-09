import asyncio
import logging
from .config import settings
from .db import init_db, mark_processed
from .listener import get_new_tweets
from .engine import process_tweet
from .gatekeeper import should_engage
from .speaker import stealth_post_worker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

background_tasks = set()

async def run_listener_cycle():
    logger.info("Starting Nitter polling cycle...")
    async for tweet in get_new_tweets():
        logger.info(f"New tweet found! ID: {tweet['id']} | Author: {tweet['username']}")
        
        # Always mark processed immediately so we don't reply twice or get stuck in retry loops
        await mark_processed(tweet['id'])
        
        engage = await should_engage(tweet['text'])
        if not engage:
            logger.info(f"Gatekeeper bypassed tweet ID: {tweet['id']}")
            continue
        
        reply, delay = await process_tweet(tweet)
        
        if reply:
            logger.info(f"Generated reply (Delay: {delay}m): {reply}")
            # Dispatch background worker and hold strong reference
            task = asyncio.create_task(stealth_post_worker(tweet['link'], reply, delay))
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)
        else:
            logger.info(f"No reply generated for tweet ID: {tweet['id']}")

async def main():
    logger.info("Initializing X-Bridge Database...")
    await init_db()
    
    logger.info(f"X-Bridge Started. Polling every {settings.poll_interval_minutes} minutes.")
    
    while True:
        try:
            await run_listener_cycle()
        except Exception as e:
            logger.error(f"Error during listener cycle: {e}")
            
        logger.info(f"Cycle complete. Sleeping for {settings.poll_interval_minutes} minutes...")
        await asyncio.sleep(settings.poll_interval_minutes * 60)

if __name__ == "__main__":
    asyncio.run(main())
