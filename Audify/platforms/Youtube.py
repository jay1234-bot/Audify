import aiohttp
import config
from youtubesearchpython.__future__ import VideosSearch


# 🔥 FINAL STREAM FETCH (JSON PARSE FIXED)
async def fetch_stream_url(link: str, video: bool = False):
    api_url = config.API_URL
    api_key = config.API_KEY

    if video:
        url = f"{api_url}/video-stream?token={api_key}&q={link}"
    else:
        url = f"{api_url}/stream?token={api_key}&q={link}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()

                    # 🔥 HANDLE MULTIPLE API FORMATS
                    if video:
                        return (
                            data.get("video")
                            or data.get("video_url")
                            or data.get("url")
                        )
                    else:
                        return (
                            data.get("audio")
                            or data.get("audio_url")
                            or data.get("url")
                        )

        except Exception as e:
            print("API ERROR:", e)

    return None


class YouTubeAPI:

    # 🔥 FIXED (required by bot)
    async def url(self, message):
        if message.reply_to_message:
            if message.reply_to_message.text:
                return message.reply_to_message.text

        if message.text:
            text = message.text.split(None, 1)
            if len(text) > 1:
                return text[1]

        return None

    async def exists(self, link: str):
        return "youtube" in link or "youtu.be" in link

    # 🔥 MAIN TRACK FUNCTION
    async def track(self, link: str):
        results = VideosSearch(link, limit=1)
        result = (await results.next())["result"][0]

        yt_link = result["link"]

        # 🔥 GET STREAM
        stream_url = await fetch_stream_url(yt_link)

        if not stream_url:
            raise Exception("❌ No stream URL found")

        return {
            "title": result["title"],
            "link": yt_link,
            "vidid": result["id"],
            "duration_min": result["duration"],
            "thumb": result["thumbnails"][0]["url"],
            "path": stream_url,   # 🔥 REQUIRED
            "file": stream_url,   # 🔥 REQUIRED
        }, result["id"]

    # 🔥 VIDEO STREAM
    async def video(self, link: str):
        stream = await fetch_stream_url(link, True)
        if stream:
            return 1, stream
        return 0, "Failed"
