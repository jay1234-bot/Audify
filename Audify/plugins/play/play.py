import random
import string

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from Audify import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app
from Audify.core.call import Audify
from Audify.utils import seconds_to_min, time_to_seconds
from Audify.utils.channelplay import get_channeplayCB
from Audify.utils.decorators.language import languageCB
from Audify.utils.decorators.play import PlayWrapper
from Audify.utils.formatters import formats
from Audify.utils.inline import (
    botplaylist_markup,
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from Audify.utils.logger import play_logs
from Audify.utils.stream.stream import stream
from config import BANNED_USERS, lyrical


# 🔥 STREAM FIX HELPER
def fix_stream(details):
    if isinstance(details, dict):
        path = details.get("path")
        if path and str(path).startswith("http"):
            details["file"] = path
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

    # ================= URL / YOUTUBE =================
    if url:
        try:
            details, track_id = await YouTube.track(url)
        except:
            return await mystic.edit_text(_["play_3"])

        details = fix_stream(details)

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
        details, track_id = await YouTube.track(query)
    except:
        return await mystic.edit_text(_["play_3"])

    details = fix_stream(details)

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
