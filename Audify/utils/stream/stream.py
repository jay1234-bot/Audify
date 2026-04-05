import os
from random import randint
from typing import Union

from pyrogram.types import InlineKeyboardMarkup

import config
from Audify import Carbon, YouTube, app
from Audify.core.call import Audify
from Audify.misc import db
from Audify.utils.database import add_active_video_chat, is_active_chat
from Audify.utils.exceptions import AssistantErr
from Audify.utils.inline import aq_markup, close_markup, stream_markup
from Audify.utils.pastebin import AudifyBin
from Audify.utils.stream.queue import put_queue, put_queue_index
from Audify.utils.thumbnails import get_thumb


# 🔥 STREAM HELPER
def get_file(result):
    if isinstance(result, dict):
        return result.get("file") or result.get("path")
    return result


async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    if not result:
        return

    if forceplay:
        await Audify.force_stop_stream(chat_id)

    # 🔥 GET STREAM URL
    file_path = get_file(result)

    if not file_path:
        raise AssistantErr("❌ No stream URL found")

    # ================= YOUTUBE =================
    if streamtype == "youtube":
        title = result["title"]
        duration_min = result["duration_min"]
        thumbnail = result["thumb"]

        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                "stream",
                user_id,
                "video" if video else "audio",
            )
        else:
            if not forceplay:
                db[chat_id] = []

            await Audify.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=True if video else None,
                image=thumbnail,
            )

            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                "stream",
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )

            button = stream_markup(_, chat_id)

            await app.send_photo(
                original_chat_id,
                photo=thumbnail,
                caption=f"▶️ Playing: {title}",
                reply_markup=InlineKeyboardMarkup(button),
            )

    # ================= TELEGRAM =================
    elif streamtype == "telegram":
        title = result["title"]
        duration_min = result["dur"]

        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                "telegram",
                user_id,
                "video" if video else "audio",
            )
        else:
            if not forceplay:
                db[chat_id] = []

            await Audify.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=True if video else None,
            )

            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                "telegram",
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )

    # ================= INDEX =================
    elif streamtype == "index":
        if await is_active_chat(chat_id):
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index",
                "Live Stream",
                "00:00",
                user_name,
                file_path,
                "video" if video else "audio",
            )
        else:
            if not forceplay:
                db[chat_id] = []

            await Audify.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=True if video else None,
            )

            await put_queue_index(
                chat_id,
                original_chat_id,
                "index",
                "Live Stream",
                "00:00",
                user_name,
                file_path,
                "video" if video else "audio",
                forceplay=forceplay,
            )

            button = stream_markup(_, chat_id)

            await app.send_photo(
                original_chat_id,
                photo=config.STREAM_IMG_URL,
                caption="▶️ Streaming Started",
                reply_markup=InlineKeyboardMarkup(button),
            )

            await mystic.delete()
