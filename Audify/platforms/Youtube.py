import aiohttp
import config
from youtubesearchpython.__future__ import VideosSearch


async def fetch_stream_url(link: str, video: bool = False):
    api_url = config.API_URL
    api_key = config.API_KEY

    if video:
        url = f"{api_url}/video-stream?token={api_key}&q={link}"
    else:
        url = f"{api_url}/stream?token={api_key}&q={link}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, allow_redirects=True) as resp:
                if resp.status == 200:
                    return str(resp.url)
        except Exception as e:
            print("API ERROR:", e)

    return None


class YouTubeAPI:
    async def exists(self, link: str):
        return "youtube" in link or "youtu.be" in link

    async def track(self, link: str):
        results = VideosSearch(link, limit=1)
        result = (await results.next())["result"][0]

        yt_link = result["link"]

        # 🔥 STREAM FETCH
        stream_url = await fetch_stream_url(yt_link)

        if not stream_url:
            raise Exception("No stream URL")

        return {
            "title": result["title"],
            "link": yt_link,
            "vidid": result["id"],
            "duration_min": result["duration"],
            "thumb": result["thumbnails"][0]["url"],
            "path": stream_url,   # 🔥 IMPORTANT
            "file": stream_url,   # 🔥 IMPORTANT
        }, result["id"]

    async def video(self, link: str):
        stream = await fetch_stream_url(link, True)
        if stream:
            return 1, stream
        return 0, "Failed"
