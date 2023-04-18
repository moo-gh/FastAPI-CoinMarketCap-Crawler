def format_coin_message(coin, position):
    """Format single coin data for Telegram message"""
    symbol = coin["symbol"]
    price = coin["price"]
    currency = coin["currency"]

    # Add emoji based on position (green for top 10, red for others)
    emoji = "🟢" if position <= 10 else "🔴"

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
