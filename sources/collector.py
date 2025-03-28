import aiohttp
import json
from typing import Dict, List, Optional
from sources.cache import RedisCache
from config import settings

class EmojiCollector:
    BASE_URL = settings.EMOJIS_API_URL
    
    def __init__(self):
        self.cache = RedisCache()
        self.headers = {
            "accept": "application/graphql-response+json, application/json",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site"
        }

    async def search_emojis(self, query: str, first: int = 56, after: Optional[str] = None) -> Dict:
        """
        Search for emojis using the emojis.com GraphQL API
        """
        # Try to get from cache first
        cache_key = self.cache.get_search_key(query, first)
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result

        variables = {
            "query": query,
            "first": first,
            "after": after
        }
        
        query = """
        query GetSearchEmojis($query: String $first: Int $after: String) {
            searchEmojis(query: $query first: $first after: $after) {
                pageInfo {
                    endCursor
                    hasNextPage
                }
                nodes {
                    slug
                    id
                    noBackgroundUrl
                    noBackgroundUrl540
                    prompt
                }
            }
        }
        """
        
        params = {
            "query": query,
            "variables": json.dumps(variables),
            "operationName": "GetSearchEmojis"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL, headers=self.headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    # Cache the result
                    await self.cache.set(cache_key, result)
                    return result
                else:
                    raise Exception(f"API request failed with status {response.status}")

    async def get_emoji_details(self, emoji_id: str) -> Dict:
        """
        Get detailed information about a specific emoji
        """
        query = """
        query GetEmoji($id: ID!) {
            emoji(id: $id) {
                id
                createdAt
                slug
                prompt
                visibility
                noBackgroundUrl
                noBackgroundUrl540
                noBackgroundUrl128Png
                status
                vote
                voteCount
                favorited
                canDelete
                kind
                tags
                user {
                    id
                    image
                    username
                }
            }
        }
        """
        
        variables = {"id": emoji_id}
        
        params = {
            "query": query,
            "variables": json.dumps(variables),
            "operationName": "GetEmoji"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL, headers=self.headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    raise Exception(f"API request failed with status {response.status}")

    async def close(self):
        """Close the cache connection"""
        await self.cache.close()
