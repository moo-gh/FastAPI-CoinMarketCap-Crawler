import os
import redis
import logging

logger = logging.getLogger(__name__)
REDIS_URL = "redis://fastapi_crawler_redis:6379"

# Redis connection
def get_redis_client():
    """Get Redis client with connection fallback"""
    try:
        client = redis.from_url(REDIS_URL, decode_responses=True)
        # Test connection
        client.ping()
        return client
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Using fallback cache.")
        return None

def get_cached_price(symbol):
    """Get cached price for a symbol from Redis"""
    try:
        client = get_redis_client()
        if client:
            price_str = client.get(f"price:{symbol}")
            return float(price_str) if price_str else None
    except Exception as e:
        logger.error(f"Error getting cached price for {symbol}: {e}")
    return None

def set_cached_price(symbol, price):
    """Set cached price for a symbol in Redis"""
    try:
        client = get_redis_client()
        if client:
            # Cache for 24 hours (86400 seconds)
            client.setex(f"price:{symbol}", 86400, str(price))
    except Exception as e:
        logger.error(f"Error setting cached price for {symbol}: {e}")

def format_coin_message(coin, position):
    """Format single coin data for Telegram message"""
    symbol = coin["symbol"]
    price = coin["price"]
    currency = coin["currency"]

    # Get current price as float
    try:
        current_price = float(price)
    except:
        current_price = 0.0

    # Get last cached price from Redis
    last_price = get_cached_price(symbol)
    
    # Set cached price in Redis for next comparison
    set_cached_price(symbol, current_price)
    
    # Add emoji based on price comparison (green if price increased, red if decreased or same)
    if last_price is not None and current_price > last_price:
        emoji = "🟢"
    else:
        emoji = "🔴"

    # Format price with commas
    try:
        price_float = float(price)
        if price_float >= 1000:
            formatted_price = f"{price_float:,.1f}"
        else:
            formatted_price = f"{price_float:.4f}"
    except:
        formatted_price = price

    return f"{emoji} {symbol}: {formatted_price} {currency}"
