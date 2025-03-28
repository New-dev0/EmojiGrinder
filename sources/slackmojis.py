import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
from sources.cache import RedisCache
from config import settings

logger = logging.getLogger(__name__)

class SlackMojisCollector:
    BASE_URL = settings.SLACKMOJIS_BASE_URL

    def __init__(self):
        self.cache = RedisCache()
        # Cache categories for 1 day, emojis for 4 hours
        self.categories_ttl = settings.CACHE_TTL_CATEGORIES
        self.emojis_ttl = settings.CACHE_TTL_EMOJIS

    async def get_categories(self) -> List[Dict]:
        """Get all emoji categories from slackmojis.com"""
        # Try to get from cache first
        cache_key = "slackmojis:categories"
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result

        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch categories: {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                categories = []
                for group in soup.find_all('li', class_='group'):
                    title = group.find('div', class_='title')
                    if not title:
                        continue
                    
                    name = title.text.strip()
                    if name and name != "Suggest An Emoji":
                        categories.append({
                            "id": name.lower().replace(" ", "_"),
                            "name": name,
                            "url": group.find('div', class_='seemore').find('a')['href'] if group.find('div', class_='seemore') else None
                        })
                
        # Cache the results
        await self.cache.set(cache_key, categories, ttl=self.categories_ttl)
        return categories

    async def get_emojis_by_category(self, category_id: str) -> List[Dict]:
        """Get emojis for a specific category"""
        # Try to get from cache first
        cache_key = f"slackmojis:category:{category_id}"
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result

        async with aiohttp.ClientSession() as session:
            # First try to get from main page
            async with session.get(self.BASE_URL) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch emojis: {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find the category section by title
                category_title = category_id.replace("_", " ").title()
                category_section = None
                
                for group in soup.find_all('li', class_='group'):
                    title_div = group.find('div', class_='title')
                    if title_div and title_div.text.strip() == category_title:
                        category_section = group.find('ul', class_='emojis')
                        break
                
                if not category_section:
                    # If not found in main page, try the category page
                    url = f"{self.BASE_URL}/categories/{category_id}"
                    async with session.get(url) as category_response:
                        if category_response.status != 200:
                            return []
                        
                        category_html = await category_response.text()
                        category_soup = BeautifulSoup(category_html, 'html.parser')
                        category_section = category_soup.find('ul', class_='emojis')
                
                if not category_section:
                    return []
                
                emojis = []
                for emoji in category_section.find_all('li', class_='emoji'):
                    img = emoji.find('img')
                    name_div = emoji.find('div', class_='name')
                    downloader = emoji.find('a', class_='downloader')
                    
                    if img and name_div:
                        shortcode = name_div.text.strip()
                        title = name_div.get('title', '')
                        added_by = title.split(' - Added by ')[-1] if ' - Added by ' in title else 'anonymous'
                        emojis.append({
                            "name": img.get('title', '').replace(' random', '').strip(),
                            "shortcode": shortcode,
                            "url": img.get('src', ''),
                            "added_by": added_by,
                            "download_url": f"{self.BASE_URL}{downloader['href']}" if downloader else None
                        })
                
        # Cache the results
        await self.cache.set(cache_key, emojis, ttl=self.emojis_ttl)
        return emojis

    async def close(self):
        """Close the cache connection"""
        await self.cache.close() 