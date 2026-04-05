import asyncio
import os
import re
import json
import glob
import random
import logging
import aiohttp
import config
import time
import requests
import yt_dlp
from pathlib import Path
from typing import Union
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType
from youtubesearchpython.__future__ import VideosSearch
from Audify.utils.database import is_on_off
from Audify.utils.formatters import time_to_seconds


# ================== 🔥 FIXED STREAM FUNCTION ==================

async def fetch_stream_url(link: str, video: bool = False) -> str | None:
    api_key = getattr(config, "API_KEY", None)
    api_url = getattr(config, "API_URL", None)

    if not api_key or not api_url:
        raise RuntimeError("❌ API_KEY or API_URL missing in config.")

    if video:
        url = f"{api_url}/video-stream?token={api_key}&q={link}"
    else:
        url = f"{api_url}/stream?token={api_key}&q={link}"

    print(f"🔗 Requesting ({'Video' if video else 'Audio'}): {url}")

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for attempt in range(1, 3):
            try:
                async with session.get(url, allow_redirects=True) as response:
                    if response.status == 200:
                        final_url = str(response.url)
                        print(f"✅ Stream URL ready: {final_url}")
                        return final_url
            except Exception as e:
                print(f"⚠️ Request error: {e}")

            if attempt < 2:
                await asyncio.sleep(0.5)

    return None


# ================== DOWNLOAD ==================

async def download_file(link: str, video: bool = False) -> str | None:
    video_id = link.split("v=")[-1].split("&")[0]

    folder = Path("downloads/video" if video else "downloads/audio")
    folder.mkdir(parents=True, exist_ok=True)

    ext = ".mp4" if video else ".m4a"
    filepath = folder / f"{video_id}{ext}"

    if filepath.exists():
        return str(filepath)

    stream_url = await fetch_stream_url(link, video)
    if not stream_url:
        return None

    async with aiohttp.ClientSession() as session:
        async with session.get(stream_url) as response:
            if response.status != 200:
                return None

            with open(filepath, "wb") as f:
                while True:
                    chunk = await response.content.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)

    return str(filepath)


# ================== YOUTUBE CLASS ==================

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"

    async def exists(self, link: str):
        return bool(re.search(self.regex, link))

    async def url(self, message: Message):
        return message.text if message.text else None

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
        return 0, "Failed"

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
        file = await download_file(link, video)
        return file, True
