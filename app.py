import os
import asyncio
import requests
from fastapi import FastAPI, HTTPException
from telegram import Bot
from dotenv import load_dotenv
import logging
from crawler import CoinMarketCapCrawler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CoinMarketCap Crawler", version="1.0.0")

# Initialize Telegram bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL")
bot = Bot(token=TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None

class TelegramSender:
    def __init__(self, bot_token, channel_id):
        self.bot = Bot(token=bot_token)
        self.channel_id = channel_id
    
    async def send_message(self, message):
        """Send message to Telegram channel"""
        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode="HTML"
            )
            logger.info("Message sent to Telegram successfully")
            return True
        except Exception as e:
            logger.error(f"Error sending message to Telegram: {e}")
            return False

def format_coin_message(coins):
    """Format coins data for Telegram message"""
    if not coins:
        return "No coin data available"
    
    message = "🪙 <b>Top Cryptocurrency Prices</b>\n\n"
    
    for i, coin in enumerate(coins[:50], 1):
        symbol = coin["symbol"]
        price = coin["price"]
        currency = coin["currency"]
        
        # Add emoji based on position (green for top 10, red for others)
        emoji = "🟢" if i <= 10 else "🔴"
        
        # Format price with commas
        try:
            price_float = float(price)
            if price_float >= 1000:
                formatted_price = f"{price_float:,.1f}"
            else:
                formatted_price = f"{price_float:.4f}"
        except:
            formatted_price = price
        
        message += f"{emoji} {symbol}: {formatted_price} {currency.upper()}\n"
    
    return message

@app.get("/")
async def root():
    return {"message": "CoinMarketCap Crawler API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/crawl-and-send")
async def crawl_and_send():
    """Crawl CoinMarketCap and send to Telegram"""
    if not bot or not TELEGRAM_CHANNEL:
        raise HTTPException(status_code=500, detail="Telegram configuration missing")
    
    try:
        # Crawl coins
        crawler = CoinMarketCapCrawler()
        coins = crawler.get_top_coins(50)
        
        if not coins:
            raise HTTPException(status_code=500, detail="Failed to fetch coin data")
        
        # Format message
        message = format_coin_message(coins)
        
        # Send to Telegram
        sender = TelegramSender(TELEGRAM_TOKEN, TELEGRAM_CHANNEL)
        success = await sender.send_message(message)
        
        if success:
            return {
                "status": "success",
                "message": f"Sent {len(coins)} coins to Telegram",
                "coins_count": len(coins)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send to Telegram")
            
    except Exception as e:
        logger.error(f"Error in crawl_and_send: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/coins")
async def get_coins():
    """Get top coins without sending to Telegram"""
    try:
        crawler = CoinMarketCapCrawler()
        coins = crawler.get_top_coins(50)
        
        return {
            "status": "success",
            "coins": coins,
            "count": len(coins)
        }
    except Exception as e:
        logger.error(f"Error getting coins: {e}")
        raise HTTPException(status_code=500, detail=str(e))
