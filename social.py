import os
import logging
import asyncio
from telegram import Bot

logger = logging.getLogger(__name__)


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
                chat_id=self.channel_id, text=message, parse_mode="HTML"
            )
            logger.info("Message sent to Telegram successfully")
            return True
        except Exception as e:
            logger.error(f"Error sending message to Telegram: {e}")
            return False

    async def send_multiple_messages(self, messages):
        """Send multiple messages to Telegram channel"""
        success_count = 0
        for message in messages:
            try:
                await self.bot.send_message(chat_id=self.channel_id, text=message)
                success_count += 1
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error sending message '{message}': {e}")

        logger.info(f"Sent {success_count}/{len(messages)} messages to Telegram")
        return success_count > 0
