from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sources.collector import EmojiCollector
from sources.emojis import (
    GraphQLResponse, 
    EmojiDetailGraphQLResponse,
    SlackMojiCategory,
    SlackMoji
)
from sources.slackmojis import SlackMojisCollector
import base64
from typing import List

app = FastAPI(title="Emoji Search API")

# Mount templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create collector instances
collector = EmojiCollector()
slack_collector = SlackMojisCollector()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    categories = await slack_collector.get_categories()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "categories": categories
        }
    )

@app.get("/search/{query}")
async def search_emojis(query: str, limit: int = 50):
    result = await collector.search_emojis(query=query, first=limit)
    response = GraphQLResponse(**result)
    return response.data.searchEmojis.nodes

@app.get("/emoji/{emoji_id}")
async def get_emoji_detail(emoji_id: str):
    try:
        # Decode the base64 encoded ID
        decoded_id = base64.b64decode(emoji_id).decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid emoji ID format")

    result = await collector.get_emoji_details(decoded_id)
    response = EmojiDetailGraphQLResponse(**result)
    return response.data.emoji

@app.on_event("shutdown")
async def shutdown_event():
    await collector.close()
    await slack_collector.close()

@app.get("/categories", response_model=List[SlackMojiCategory])
async def get_categories():
    """Get all available emoji categories from slackmojis.com"""
    return await slack_collector.get_categories()

@app.get("/category/{category_id}", response_model=List[SlackMoji])
async def get_category_emojis(category_id: str):
    """Get all emojis in a specific category"""
    try:
        emojis = await slack_collector.get_emojis_by_category(category_id)
        if not emojis:
            raise HTTPException(status_code=404, detail="Category not found")
        return emojis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 