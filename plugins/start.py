# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio
import os
import random
import sys
import time
import string
import string as rohit
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import *
from helper_func import *
from database.database import *

# File auto-delete time in seconds (Set your desired time in seconds here)
FILE_AUTO_DELETE = TIME  # Example: 3600 seconds (1 hour)
TUT_VID = f"{TUT_VID}"







LOG_CHANNEL_ID = -1002612670454
        
        
        

        

         
@Bot.on_message(filters.command('start') & filters.private & subscribed1 & subscribed2 & subscribed3 & subscribed4)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass

    # Verification system (unchanged)
    if id in ADMINS:
        verify_status = {
            'is_verified': True,
            'verify_token': None,
            'verified_time': time.time(),
            'link': ""
        }
    else:
        verify_status = await get_verify_status(id)

        if TOKEN:
            if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
                await update_verify_status(id, is_verified=False)

            if "verify_" in message.text:
                _, token = message.text.split("_", 1)
                if verify_status['verify_token'] != token:
                    return await message.reply("Your token is invalid or expired. Try again by clicking /start.")
                await update_verify_status(id, is_verified=True, verified_time=time.time())
                return await message.reply("Token verified ✅", quote=True)

            if not verify_status['is_verified']:
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                await update_verify_status(id, verify_token=token, link="")
                link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://telegram.dog/{client.username}?start=verify_{token}')
                btn = [
                    [InlineKeyboardButton("• ᴏᴘᴇɴ ʟɪɴᴋ •", url=link), InlineKeyboardButton('• ᴛᴜᴛᴏʀɪᴀʟ •', url=TUT_VID)],
                    [InlineKeyboardButton('• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •', callback_data='premium')]
                ]
                return await message.reply(
                    f"Token expired. Please refresh token to continue.\n\n<b>ᴛᴏᴋᴇɴ ᴛɪᴍᴇᴏᴜᴛ:</b> {get_exp_time(VERIFY_EXPIRE)}",
                    reply_markup=InlineKeyboardMarkup(btn),
                    protect_content=False,
                    quote=True
                )

    # Deep link processing
    if len(message.text) > 7:
        try:
            base64_string = message.text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")
        except:
            return

        ids = []
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
            except:
                return
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return

        temp_msg = await message.reply("<b>Please wait...</b>")
        try:
            messages = await get_messages(client, ids)
            if not messages:
                await message.reply_text("No messages found!")
                return
        except:
            await message.reply_text("Something went wrong!")
            return
        finally:
            await temp_msg.delete()

        codeflix_msgs = []
        
        async def send_media_group_safely(media_group):
            try:
                sent = await client.send_media_group(
                    chat_id=message.chat.id,
                    media=media_group,
                    protect_content=PROTECT_CONTENT
                )
                codeflix_msgs.extend(sent)
                await asyncio.sleep(5)  # 5-second delay between groups
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await send_media_group_safely(media_group)
            except:
                # Fallback to individual sends
                for media in media_group:
                    await send_individual_media(media)

        async def send_individual_media(media):
            try:
                if isinstance(media, InputMediaPhoto):
                    msg = await message.reply_photo(
                        photo=media.media,
                        caption=media.caption,
                        parse_mode=ParseMode.HTML
                    )
                elif isinstance(media, InputMediaVideo):
                    msg = await message.reply_video(
                        video=media.media,
                        caption=media.caption,
                        parse_mode=ParseMode.HTML
                    )
                elif isinstance(media, InputMediaDocument):
                    msg = await message.reply_document(
                        document=media.media,
                        caption=media.caption,
                        parse_mode=ParseMode.HTML
                    )
                codeflix_msgs.append(msg)
                await asyncio.sleep(3)  # 3-second delay between individual messages
            except:
                pass

        media_group = []
        current_type = None
        
        for msg in messages:
            if not msg:
                continue

            # Handle text messages
            if msg.text:
                if media_group:
                    await send_media_group_safely(media_group)
                    media_group = []
                try:
                    sent = await message.reply_text(msg.text.html if msg.text.html else msg.text)
                    codeflix_msgs.append(sent)
                    await asyncio.sleep(3)  # 3-second delay after text
                except:
                    pass
                continue

            # Handle media
            try:
                media = None
                if msg.photo:
                    media = InputMediaPhoto(media=msg.photo.file_id)
                    media_type = "photo"
                elif msg.video:
                    media = InputMediaVideo(media=msg.video.file_id)
                    media_type = "video"
                elif msg.document:
                    media = InputMediaDocument(media=msg.document.file_id)
                    media_type = "document"
                
                if media:
                    if CUSTOM_CAPTION and msg.document:
                        caption = CUSTOM_CAPTION.format(
                            previouscaption="" if not msg.caption else msg.caption.html,
                            filename=msg.document.file_name
                        )
                    elif msg.caption:
                        caption = msg.caption.html
                    
                    if caption:
                        media.caption = caption
                        media.parse_mode = ParseMode.HTML

                    # Start new group if type changes or limit reached
                    if (media_type != current_type) or (len(media_group) >= 10):
                        if media_group:
                            await send_media_group_safely(media_group)
                            media_group = []
                        current_type = media_type

                    media_group.append(media)
            except:
                continue

        # Send remaining media
        if media_group:
            await send_media_group_safely(media_group)

        # YOUR ORIGINAL AUTO-DELETE MESSAGE (UNCHANGED)
        if FILE_AUTO_DELETE > 0:
            notification_msg = await message.reply(
                f"<b>This file will be deleted in {get_exp_time(FILE_AUTO_DELETE)}.\nPlease download before it gets deleted.</b>"
            )
            await asyncio.sleep(FILE_AUTO_DELETE)

            for snt_msg in codeflix_msgs:
                if snt_msg:
                    try:
                        await snt_msg.delete()
                    except:
                        pass

            try:
                reload_url = (
                    f"https://t.me/{client.username}?start={message.command[1]}"
                    if message.command and len(message.command) > 1 else None
                )
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Request again", url=reload_url)]]
                ) if reload_url else None

                await notification_msg.edit(
                    "<b>All files have been deleted ✅</b>",
                    reply_markup=keyboard
                )
            except:
                pass
        return

    # Default /start response
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
         InlineKeyboardButton("ʜᴇʟᴘ •", callback_data="help")]
    ])
    await message.reply_photo(
        photo=START_PIC,
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=reply_markup
    )
    return





                





#=====================================================================================##
# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    # Initialize buttons list
    buttons = []

    # Check if the first and second channels are both set
    if FORCE_SUB_CHANNEL1 and FORCE_SUB_CHANNEL2:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink1),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink2),
        ])
    # Check if only the first channel is set
    elif FORCE_SUB_CHANNEL1:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink1)
        ])
    # Check if only the second channel is set
    elif FORCE_SUB_CHANNEL2:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink2)
        ])

    # Check if the third and fourth channels are set
    if FORCE_SUB_CHANNEL3 and FORCE_SUB_CHANNEL4:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink3),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink4),
        ])
    # Check if only the first channel is set
    elif FORCE_SUB_CHANNEL3:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink3)
        ])
    # Check if only the second channel is set
    elif FORCE_SUB_CHANNEL4:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink4)
        ])

    # Append "Try Again" button if the command has a second argument
    try:
        buttons.append([
            InlineKeyboardButton(
                text="ʀᴇʟᴏᴀᴅ",
                url=f"https://t.me/{client.username}?start={message.command[1]}"
            )
        ])
    except IndexError:
        pass  # Ignore if no second argument is present

    await message.reply_photo(
        photo=FORCE_PIC,
        caption=FORCE_MSG.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=None if not message.from_user.username else '@' + message.from_user.username,
        mention=message.from_user.mention,
        id=message.from_user.id
    ),
    reply_markup=InlineKeyboardMarkup(buttons)#,
    #message_effect_id=5104841245755180586  # Add the effect ID here
)


#=====================================================================================##

WAIT_MSG = "<b>Working....</b>"

REPLY_ERROR = "<code>Use this command as a reply to any telegram message without any spaces.</code>"

#=====================================================================================##


@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await message.reply("<i>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴏᴄᴇꜱꜱɪɴɢ....</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1

        status = f"""<b><u>ʙʀᴏᴀᴅᴄᴀꜱᴛ...</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()

# broadcast with auto-del

@Bot.on_message(filters.private & filters.command('dbroadcast') & filters.user(ADMINS))
async def delete_broadcast(client: Bot, message: Message):
    if message.reply_to_message:
        try:
            duration = int(message.command[1])  # Get the duration in seconds
        except (IndexError, ValueError):
            await message.reply("<b>Please provide a valid duration in seconds.</b> Usage: /dbroadcast {duration}")
            return

        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await message.reply("<i>Broadcast with auto-delete processing....</i>")
        for chat_id in query:
            try:
                sent_msg = await broadcast_msg.copy(chat_id)
                await asyncio.sleep(duration)  # Wait for the specified duration
                await sent_msg.delete()  # Delete the message after the duration
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                sent_msg = await broadcast_msg.copy(chat_id)
                await asyncio.sleep(duration)
                await sent_msg.delete()
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1

        status = f"""<b><u>Broadcast with Auto-Delete...</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

        return await pls_wait.edit(status)

    else:
        msg = await message.reply("Please reply to a message to broadcast it with auto-delete.")
        await asyncio.sleep(8)
        await msg.delete()
