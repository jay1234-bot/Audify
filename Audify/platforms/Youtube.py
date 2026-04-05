import asyncio
import re
import aiohttp
import config
from typing import Union
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType
from youtubesearchpython.__future__ import VideosSearch
from Audify.utils.formatters import time_to_seconds

# ================= STREAM FUNCTION =================

async def fetch_stream_url(link: str, video: bool = False) -> str | None:
    api_key = getattr(config, "API_KEY", None)
    api_url = getattr(config, "API_URL", None)

    if not api_key or not api_url:
        print("❌ API config missing")
        return None

    if video:
        url = f"{api_url}/video-stream?token={api_key}&q={link}"
    else:
        url = f"{api_url}/stream?token={api_key}&q={link}"

    print(f"🔗 Requesting: {url}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, allow_redirects=True) as resp:
                if resp.status == 200:
                    return str(resp.url)
                else:
                    print(f"❌ API Error: {resp.status}")
        except Exception as e:
            print(f"❌ Request failed: {e}")

    return None


# ================= DOWNLOAD (STREAM BASED) =================

async def download_file(link: str, video: bool = False):
    stream = await fetch_stream_url(link, video)
    return stream  # 🔥 always return stream


# ================= YOUTUBE CLASS =================

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"

    async def exists(self, link: str):
        return bool(re.search(self.regex, link))

    async def url(self, message: Message):
        if message.text:
            return message.text
        return None

    async def details(self, link: str):
        results = VideosSearch(link, limit=1)
        result = (await results.next())["result"][0]

        return (
            result["title"],
            result["duration"],
            int(time_to_seconds(result["duration"])) if result["duration"] else 0,
            result["thumbnails"][0]["url"],
            result["id"],
        )

    async def video(self, link: str):
        stream = await fetch_stream_url(link, video=True)
        if stream:
            return 1, stream
        return 0, "Failed to fetch video"

    async def track(self, link: str):
        results = VideosSearch(link, limit=1)
        result = (await results.next())["result"][0]

        return {
            "title": result["title"],
            "link": result["link"],
            "vidid": result["id"],
            "duration_min": result["duration"],
            "thumb": result["thumbnails"][0]["url"],
        }, result["id"]

    async def download(self, link: str, mystic, video=False):
        stream = await download_file(link, video)

        if not stream:
            return None, False

        # 🔥 IMPORTANT FIX (no FileNotFoundError)
        return stream, False
