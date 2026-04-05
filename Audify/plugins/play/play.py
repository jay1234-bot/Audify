import random
import string

from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from Audify import YouTube, app
from Audify.utils.decorators.play import PlayWrapper
from Audify.utils.logger import play_logs
from Audify.utils.stream.stream import stream
from config import BANNED_USERS


# 🔥 FINAL STREAM FIX (FORCE API)
async def force_stream(details):
    try:
        # already stream hai
        if details.get("file"):
            return details

        # 🔥 FORCE API CALL
        stream_data = await YouTube.video(details["link"])

        if isinstance(stream_data, tuple):
            stream_url = stream_data[1]
        else:
            stream_url = stream_data

        details["file"] = stream_url
        details["path"] = stream_url

    except Exception as e:
        print("FORCE STREAM ERROR:", e)

    return details


@app.on_message(
    filters.command(
        ["play", "vplay", "cplay", "cvplay", "playforce", "vplayforce", "cplayforce", "cvplayforce"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & filters.group
    & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(
    client,
    message: Message,
    _,
    chat_id,
    video,
    channel,
    playmode,
    url,
    fplay,
):
    mystic = await message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )

    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # ================= URL =================
    if url:
        try:
            details, _ = await YouTube.track(url)
        except:
            return await mystic.edit_text(_["play_3"])

        # 🔥 FORCE STREAM FIX
        details = await force_stream(details)

        try:
            await stream(
                _,
                mystic,
                user_id,
                details,
                chat_id,
                user_name,
                message.chat.id,
                video=video,
                streamtype="youtube",
                forceplay=fplay,
            )
        except Exception as e:
            return await mystic.edit_text(str(e))

        await mystic.delete()
        return await play_logs(message, streamtype="youtube")

    # ================= SEARCH =================
    if len(message.command) < 2:
        return await mystic.edit_text(_["play_18"])

    query = message.text.split(None, 1)[1]

    try:
        details, _ = await YouTube.track(query)
    except:
        return await mystic.edit_text(_["play_3"])

    # 🔥 FORCE STREAM FIX
    details = await force_stream(details)

    try:
        await stream(
            _,
            mystic,
            user_id,
            details,
            chat_id,
            user_name,
            message.chat.id,
            video=video,
            streamtype="youtube",
            forceplay=fplay,
        )
    except Exception as e:
        return await mystic.edit_text(str(e))

    await mystic.delete()
    return await play_logs(message, streamtype="youtube")
