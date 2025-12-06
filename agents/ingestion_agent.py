# agents/ingestion.py
import aiohttp
import asyncio
import json
import os
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

class NewsIngestionAgent:
    def __init__(self):
        self.api_key = os.getenv("NEWSAPI_KEY")
        self.session = None
        self.cache = {}  # encrypted cache

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def fetch_news(self, query: str):
        session = await self._get_session()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Secure-TradlBot/1.0"
        }
        url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt"
        
        try:
            async with session.get(url, headers=headers, timeout=10) as resp:
                data = await resp.json()
                articles = data.get("articles", [])
                # Encrypt cache
                from main_orchestrator import TradlOrchestrator
                enc = TradlOrchestrator().fernet.encrypt(json.dumps(articles).encode()).decode()
                self.cache[query] = enc
                logger.info(f"Fetched {len(articles)} articles for {query}")
                return articles
        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            return []

    async def batch_process(self, queries):
        tasks = [self.fetch_news(q) for q in queries]
        results = await asyncio.gather(*tasks)
        return [art for sublist in results for art in sublist]
