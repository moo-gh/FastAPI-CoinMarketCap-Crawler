import asyncio
import aiohttp
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoinScheduler:
    def __init__(
        self, 
        api_url="http://localhost:8000", 
        interval_minutes=30, 
        api_token=None,
        specific_coins=None
    ):
        self.api_url = api_url
        self.interval_minutes = interval_minutes
        self.api_token = api_token
        self.specific_coins = specific_coins or ["BTC", "ETH", "BNB", "SOL", "TON", "PAXG", "KAG"]
        self.running = False

    async def send_update(self):
        """Send coin update to Telegram"""
        try:
            headers = {}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            
            # Use specific coins endpoint
            symbols = ",".join(self.specific_coins)
            url = f"{self.api_url}/crawl-and-send/specific?symbols={symbols}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Update sent successfully: {result}")
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send update: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error sending update: {e}")

    async def run_scheduler(self):
        """Run the scheduler loop"""
        self.running = True
        logger.info(f"Starting scheduler with {self.interval_minutes} minute intervals")
        logger.info(f"Tracking coins: {', '.join(self.specific_coins)}")

        while self.running:
            try:
                await self.send_update()
                logger.info(
                    f"Waiting {self.interval_minutes} minutes until next update..."
                )
                await asyncio.sleep(self.interval_minutes * 60)
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                self.running = False
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    def stop(self):
        """Stop the scheduler"""
        self.running = False


async def main():
    # Get interval from environment or use default
    interval = int(os.getenv("UPDATE_INTERVAL_MINUTES", "30"))
    api_url = os.getenv("API_URL", "http://localhost:8000")
    api_token = os.getenv("API_TOKEN")
    
    # Get specific coins from environment or use default
    coins_env = os.getenv("TRACKED_COINS")
    specific_coins = None
    if coins_env:
        specific_coins = [coin.strip().upper() for coin in coins_env.split(",")]
    
    if not api_token:
        logger.error("API_TOKEN environment variable is required")
        return

    scheduler = CoinScheduler(
        api_url=api_url, 
        interval_minutes=interval, 
        api_token=api_token,
        specific_coins=specific_coins
    )

    try:
        await scheduler.run_scheduler()
    except KeyboardInterrupt:
        logger.info("Shutting down scheduler...")
        scheduler.stop()


if __name__ == "__main__":
    asyncio.run(main())
