from pyrogram import Client, filters
from pymongo import MongoClient

# MongoDB connection
mongo = MongoClient("mongodb+srv://monish280720:hsUe1KPZd5wh5hfD@cluster0.x2rr3kl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo["filestore"]
named_links = db["named_links"]

# /save command to save a link with a name
@Client.on_message(filters.command("save") & filters.reply & filters.private)
async def save_named_link(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: Reply to a forwarded file and type:\n`/save your_custom_name`")

    name = message.command[1].lower()
    if not message.reply_to_message or not message.reply_to_message.forward_from_chat:
        return await message.reply("Please reply to a **forwarded message** from the file store channel.")

    try:
        file_link = await message.reply_to_message.forward(copy=True)
        link = f"https://t.me/{file_link.chat.username}/{file_link.message_id}"

        named_links.update_one(
            {"name": name},
            {"$set": {"link": link}},
            upsert=True
        )
        await message.reply(f"Link saved under name `{name}`:\n{link}")
    except Exception as e:
        await message.reply(f"Error saving link: {e}")

# /get command to retrieve the link using the saved name
@Client.on_message(filters.command("get") & filters.private)
async def get_named_link(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: `/get your_custom_name`")

    name = message.command[1].lower()
    result = named_links.find_one({"name": name})
    if result:
        await message.reply(f"Here is your link for `{name}`:\n{result['link']}")
    else:
        await message.reply("No link found with that name.")#(©)Codexbotz

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(text = "Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue

    while True:
        try:
            second_message = await client.ask(text = "Forward the Last Message from DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue


    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(text = "Forward Message from the DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote = True)
            continue

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)
