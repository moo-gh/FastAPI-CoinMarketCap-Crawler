import logging

from dotenv import load_dotenv
from fastapi import Query
from fastapi import FastAPI, HTTPException

from utils import format_coin_message
from crawler import CoinMarketCapCrawler
from social import bot, TELEGRAM_CHANNEL, TELEGRAM_TOKEN, TelegramSender


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CoinMarketCap Crawler", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "CoinMarketCap Crawler API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/crawl-and-send")
async def crawl_and_send(
    send_multiple: bool = Query(
        False,
        description="If true, send each coin as a separate message. If false (default), send all coins in one message.",
    ),
    max_coins: int = Query(
        5,
        ge=1,
        le=50,
        description="Number of top coins to fetch and send (default: 5, max: 50).",
    ),
):
    """Crawl CoinMarketCap and send to Telegram"""
    if not bot or not TELEGRAM_CHANNEL:
        raise HTTPException(status_code=500, detail="Telegram configuration missing")

    try:
        # Crawl coins
        crawler = CoinMarketCapCrawler()
        coins = crawler.get_top_coins(max_coins)

        if not coins:
            raise HTTPException(status_code=500, detail="Failed to fetch coin data")

        sender = TelegramSender(TELEGRAM_TOKEN, TELEGRAM_CHANNEL)

        if send_multiple:
            # Format individual messages for each coin
            messages = []
            for i, coin in enumerate(coins[:max_coins], 1):
                message = format_coin_message(coin, i)
                messages.append(message)
            success = await sender.send_multiple_messages(messages)
            sent_count = len(messages)
        else:
            # Send all coins in one message
            message_lines = [
                format_coin_message(coin, i)
                for i, coin in enumerate(coins[:max_coins], 1)
            ]
            full_message = "\n".join(message_lines)
            await sender.bot.send_message(chat_id=TELEGRAM_CHANNEL, text=full_message)
            success = True
            sent_count = 1

        if success:
            return {
                "status": "success",
                "message": (
                    f"Sent {len(coins) if not send_multiple else sent_count} "
                    f"{'coin prices in one message' if not send_multiple else 'messages'} to Telegram"
                ),
                "coins_count": len(coins),
                "messages_sent": sent_count,
                "send_multiple": send_multiple,
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

        return {"status": "success", "coins": coins, "count": len(coins)}
    except Exception as e:
        logger.error(f"Error getting coins: {e}")
        raise HTTPException(status_code=500, detail=str(e))
