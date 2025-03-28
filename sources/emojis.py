from pydantic import BaseModel
from typing import List, Optional

class EmojiPageInfo(BaseModel):
    endCursor: str
    hasNextPage: bool

class Emoji(BaseModel):
    slug: str
    id: str
    noBackgroundUrl: str
    noBackgroundUrl540: str
    prompt: str

class SearchEmojiResponse(BaseModel):
    pageInfo: EmojiPageInfo
    nodes: List[Emoji]

class SearchData(BaseModel):
    searchEmojis: SearchEmojiResponse

class GraphQLResponse(BaseModel):
    data: SearchData

class EmojiUser(BaseModel):
    id: str
    image: Optional[str]
    username: str

class Complaint(BaseModel):
    id: str
    reason: str

class EmojiDetail(BaseModel):
    id: str
    createdAt: str
    slug: str
    prompt: str
    visibility: str
    noBackgroundUrl: str
    noBackgroundUrl540: str
    noBackgroundUrl128Png: str
    status: str
    vote: Optional[int]
    voteCount: int
    favorited: bool
    canDelete: bool
    kind: str
    tags: List[str]
    complaint: Optional[Complaint] = None
    user: Optional[EmojiUser] = None

class EmojiDetailResponse(BaseModel):
    emoji: EmojiDetail

class EmojiDetailGraphQLResponse(BaseModel):
    data: EmojiDetailResponse

class SlackMojiCategory(BaseModel):
    id: str
    name: str
    url: Optional[str]

class SlackMoji(BaseModel):
    name: str
    shortcode: str
    url: str
    added_by: str
    download_url: str
