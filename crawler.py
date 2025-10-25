import os
import requests
import logging
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict

logger = logging.getLogger(__name__)


class CoinMarketCapCrawler:
    def __init__(self):
        self.api_key = os.getenv("CMC_API_KEY")
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
        self.headers = (
            {"X-CMC_PRO_API_KEY": self.api_key, "Accept": "application/json"}
            if self.api_key
            else {}
        )

    def get_top_coins(self, limit: int = 50) -> List[Dict]:
        """Get top coins by market cap using CoinMarketCap API"""
        try:
            if not self.api_key:
                logger.warning("No API key provided, using fallback method")
                return self._fallback_crawl(limit)

            url = f"{self.base_url}/cryptocurrency/listings/latest"
            params = {"limit": limit, "convert": "USD"}

            response = requests.get(
                url, headers=self.headers, params=params, timeout=10
            )
            response.raise_for_status()

            data = response.json()
            coins = []

            for coin in data.get("data", []):
                symbol = coin.get("symbol", "")
                price = coin.get("quote", {}).get("USD", {}).get("price", 0)

                if symbol and price:
                    coins.append(
                        {"symbol": symbol, "price": str(price), "currency": "usdt"}
                    )

            return coins

        except Exception as e:
            logger.error(f"Error fetching from API: {e}")
            return self._fallback_crawl(limit)

    def get_specific_coins(self, symbols: List[str]) -> List[Dict]:
        """Get specific coins by their symbols (e.g., ['BTC', 'TON', 'SOL'])"""
        try:
            if not self.api_key:
                logger.warning("No API key provided, cannot fetch specific coins")
                return self._fallback_specific_coins(symbols)

            url = f"{self.base_url}/cryptocurrency/quotes/latest"
            # Join symbols with comma for API request
            symbol_param = ",".join(symbols)
            params = {"symbol": symbol_param, "convert": "USD"}

            response = requests.get(
                url, headers=self.headers, params=params, timeout=10
            )
            response.raise_for_status()

            data = response.json()
            coins = []

            # The response data is keyed by symbol
            for symbol in symbols:
                coin_data = data.get("data", {}).get(symbol)
                if coin_data:
                    price = coin_data.get("quote", {}).get("USD", {}).get("price", 0)
                    if price:
                        coins.append(
                            {"symbol": symbol, "price": str(price), "currency": "usdt"}
                        )
                else:
                    logger.warning(f"No data found for symbol: {symbol}")

            return coins

        except Exception as e:
            logger.error(f"Error fetching specific coins from API: {e}")
            return self._fallback_specific_coins(symbols)

    def _fallback_specific_coins(self, symbols: List[str]) -> List[Dict]:
        """Fallback method for getting specific coins using web scraping"""
        try:
            # Fetch all coins first
            all_coins = self._fallback_crawl(limit=200)

            # Filter to only requested symbols
            symbols_upper = [s.upper() for s in symbols]
            specific_coins = [
                coin for coin in all_coins 
                if coin.get("symbol", "").upper() in symbols_upper
            ]
            return specific_coins

        except Exception as e:
            logger.error(f"Error in fallback specific coins: {e}")
            return []

    def _fallback_crawl(self, limit: int = 50) -> List[Dict]:
        """Fallback method using web scraping"""
        try:
            url = "https://coinmarketcap.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            coins = []

            # Try to find coin data in the page
            # Look for script tags with JSON data
            scripts = soup.find_all("script")
            for script in scripts:
                if script.string and "window.__APOLLO_STATE__" in script.string:
                    # Extract JSON data from Apollo state
                    json_match = re.search(
                        r"window\.__APOLLO_STATE__\s*=\s*({.*?});",
                        script.string,
                        re.DOTALL,
                    )
                    if not json_match:
                        continue
                    try:
                        apollo_data = json.loads(json_match.group(1))
                        # Parse Apollo state to extract coin data
                        coins = self._parse_apollo_data(apollo_data, limit)
                        if coins:
                            return coins
                    except:
                        continue

            # If Apollo parsing fails, try table parsing
            return self._parse_table(soup, limit)

        except Exception as e:
            logger.error(f"Error in fallback crawl: {e}")
            return []

    def _parse_apollo_data(self, apollo_data: dict, limit: int) -> List[Dict]:
        """Parse Apollo state data to extract coin information"""
        coins = []
        try:
            # Look for cryptocurrency data in Apollo state
            for key, value in apollo_data.items():
                if isinstance(value, dict) and "symbol" in value and "quote" in value:
                    symbol = value.get("symbol", "")
                    quote = value.get("quote", {})
                    price = quote.get("USD", {}).get("price", 0)

                    if symbol and price:
                        coins.append(
                            {"symbol": symbol, "price": str(price), "currency": "usdt"}
                        )

                        if len(coins) >= limit:
                            break

            return coins
        except Exception as e:
            logger.error(f"Error parsing Apollo data: {e}")
            return []

    def _parse_table(self, soup, limit: int) -> List[Dict]:
        """Parse HTML table to extract coin data"""
        coins = []
        try:
            # Look for table with coin data
            tables = soup.find_all("table")

            for table in tables:
                rows = table.find_all("tr")[1 : limit + 1]  # Skip header

                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 3:
                        # Try to extract symbol and price
                        symbol_cell = cells[1] if len(cells) > 1 else cells[0]
                        price_cell = cells[2] if len(cells) > 2 else cells[1]

                        symbol = symbol_cell.get_text(strip=True).split()[0]
                        price_text = price_cell.get_text(strip=True)
                        price = price_text.replace("$", "").replace(",", "")

                        if symbol and price and price != "N/A":
                            try:
                                float(price)  # Validate price
                                coins.append(
                                    {
                                        "symbol": symbol,
                                        "price": price,
                                        "currency": "usdt",
                                    }
                                )
                            except:
                                continue

                        if len(coins) >= limit:
                            break

                if coins:
                    break

            return coins
        except Exception as e:
            logger.error(f"Error parsing table: {e}")
            return []
