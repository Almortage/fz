from pyrogram import Client, filters
from youtubesearchpython.__future__ import VideosSearch 
import os
import aiohttp
import requests
import random 
import asyncio
import yt_dlp
from datetime import datetime, timedelta
from youtube_search import YoutubeSearch
import pytgcalls
from pytgcalls.types.input_stream.quality import (HighQualityAudio,
                                                  HighQualityVideo,
                                                  LowQualityAudio,
                                                  LowQualityVideo,
                                                  MediumQualityAudio,
                                                  MediumQualityVideo)
from typing import Union
from pyrogram import Client, filters 
from pyrogram import Client as client
from pyrogram.errors import (ChatAdminRequired,
                             UserAlreadyParticipant,
                             UserNotParticipant)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType, ChatMemberStatus
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import (AlreadyJoinedError,
                                  NoActiveGroupCall,
                                  TelegramServerError)
from pytgcalls.types import (JoinedGroupCallParticipant,
                             LeftGroupCallParticipant, Update)
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.stream import StreamAudioEnded
from config import API_ID, API_HASH, MONGO_DB_URL, PHOTO, OWNER, OWNER_NAME, LOGS, GROUP, CHANNEL
from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_
from pymongo import MongoClient
from bot import bot as man
from SEMO.info import (db, add, is_served_call, add_active_video_chat, add_served_call, add_active_chat, gen_thumb, download, remove_active, joinch)
from SEMO.Data import (get_logger, get_userbot, get_call, get_logger_mode, get_group, get_channel)
import asyncio
             
mongodb = _mongo_client_(MONGO_DB_URL)
pymongodb = MongoClient(MONGO_DB_URL)
Bots = pymongodb.Bots


async def join_assistant(client, chat_id, message_id, userbot, file_path):
        join = None
        try:
            try:
                user = userbot.me
                user_id = user.id
                get = await client.get_chat_member(chat_id, user_id)
            except ChatAdminRequired:
                await client.send_message(chat_id, f"**قم بترقية البوت مشرف ..**", reply_to_message_id=message_id)
            if get.status == ChatMemberStatus.BANNED:
                await client.send_message(chat_id, f"**قم بالغاء الحظر عن الحساب المساعد لتفعيل البوت**.\n\n @{user.username} : **الحساب المساعد **..\n** قم بتنظيف قايمه المستدخمين تمت ازالتهم ..**\n\n** @T_S_T1 : او تواصل مع المطور من هنا ..**", reply_to_message_id=message_id)
            else:
              join = True
        except UserNotParticipant:
            chat = await client.get_chat(chat_id)
            if chat.username:
                try:
                    await userbot.join_chat(chat.username)
                    join = True
                except UserAlreadyParticipant:
                    join = True
                except Exception:
                 try:
                  invitelink = (await client.export_chat_invite_link(chat_id))
                  if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
                  await asyncio.sleep(3)
                  await userbot.join_chat(invitelink)
                  join = True
                 except ChatAdminRequired:
                    return await client.send_message(chat_id, f"**قم اعطاء البوت صلاحيه اضافه المستخدمين عبر الرابط ..**", reply_to_message_id=message_id)
                 except Exception as e:
                   await client.send_message(chat_id, f"** حدث خطأ حاول مرا آخري لاحقا**\n**{GROUP} : او تواصل مع الدعم من هنا ..**", reply_to_message_id=message_id)
            else:
                try:
                    try:
                       invitelink = chat.invite_link
                       if invitelink is None:
                          invitelink = (await client.export_chat_invite_link(chat_id))
                    except Exception:
                        try:
                          invitelink = (await client.export_chat_invite_link(chat_id))
                        except ChatAdminRequired:
                          await client.send_message(chat_id, f"**قم اعطاء البوت صلاحيه اضافه مستخدمين عبر الرابط ..**", reply_to_message_id=message_id)
                        except Exception as e:
                          await client.send_message(chat_id, f"** حدث خطأ حاول مرا آخري لاحقا**\n**{GROUP} : او تواصل مع الدعم من هنا ..**", reply_to_message_id=message_id)
                    m = await client.send_message(chat_id, "**انتظر قليلاً جاري تفعيل البوت ..**")
                    if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
                    await userbot.join_chat(invitelink)
                    join = True
                    await m.edit(f"**{user.mention} : انضم الحساب المساعد **\n**وتم تفعيل البوت يمكنك التشغيل الان ..**")
                except UserAlreadyParticipant:
                    join = True
                except Exception as e:
                    await client.send_message(chat_id, f"** حدث خطأ حاول مرا آخري لاحقا**\n**{GROUP} : او تواصل مع الدعم من هنا ..**", reply_to_message_id=message_id)
        return join        

async def join_call(
        client,
        message_id,
        chat_id,
        bot_username,
        file_path,
        link,
        vid: Union[bool, str] = None):
        userbot = await get_userbot(bot_username)
        Done = None
        try:
          call = await get_call(bot_username)
        except:
          return Done
        file_path = file_path
        audio_stream_quality = MediumQualityAudio()
        video_stream_quality = MediumQualityVideo()
        stream = (AudioVideoPiped(file_path, audio_parameters=audio_stream_quality, video_parameters=video_stream_quality) if vid else AudioPiped(file_path, audio_parameters=audio_stream_quality))
        try:
            await call.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
            Done = True
        except NoActiveGroupCall:
                 h = await join_assistant(client, chat_id, message_id, userbot, file_path)
                 if h:
                  try:
                   await call.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
                   Done = True
                  except Exception:
                      await client.send_message(chat_id, "**قم بتشغيل المكالمة أولاً ..**", reply_to_message_id=message_id)
        except AlreadyJoinedError:
             await client.send_message(chat_id, "**قم بإعادة تشغيل المكالمة ...**", reply_to_message_id=message_id)
        except TelegramServerError:
             await client.send_message(chat_id, "**قم بإعادة تشغيل المكالمة ...**", reply_to_message_id=message_id)
        except Exception as a:
            print(a)
            return Done
        return Done

def seconds_to_min(seconds):
    if seconds is not None:
        seconds = int(seconds)
        d, h, m, s = (
            seconds // (3600 * 24),
            seconds // 3600 % 24,
            seconds % 3600 // 60,
            seconds % 3600 % 60,
        )
        if d > 0:
            return "{:02d}:{:02d}:{:02d}:{:02d}".format(d, h, m, s)
        elif h > 0:
            return "{:02d}:{:02d}:{:02d}".format(h, m, s)
        elif m > 0:
            return "{:02d}:{:02d}".format(m, s)
        elif s > 0:
            return "00:{:02d}".format(s)
    return "-"


async def logs(bot_username, client, message):
  try:
   if await get_logger_mode(bot_username) == "OFF":
     return
   logger = await get_logger(bot_username)
   log = LOGS
   if message.chat.type == ChatType.CHANNEL:
     chat = f"[{message.chat.title}](t.me/{message.chat.username})" if message.chat.username else message.chat.title
     name = f"{message.author_signature}" if message.author_signature else chat
     text = f"**Playing History **\n\n**Chat : {chat}**\n**Chat Id : {message.chat.id}**\n**User Name : {name}**\n\n**Played : {message.text}**"
   else:
     chat = f"[{message.chat.title}](t.me/{message.chat.username})" if message.chat.username else message.chat.title
     user = f"User Username : @{message.from_user.username}" if message.from_user.username else f"User Id : {message.from_user.id}"
     text = f"**Playing History **\n\n**Chat : {chat}**\n**Chat Id : {message.chat.id}**\n**User Name : {message.from_user.mention}**\n**{user}**\n\n**Played : {message.text}**"
   await client.send_message(logger, text=text, disable_web_page_preview=True)
   return await man.send_message(log, text=f"[ @{bot_username} ]\n{text}", disable_web_page_preview=True)
  except:
    pass

@Client.on_message(filters.video_chat_started)
async def brah(client: Client, message):
    await message.reply("- وهيصـه آلكول آتفتح يلآ نعمـل قلقآن فوق 😂🥹")

@Client.on_message(filters.video_chat_ended)
async def brah2(client: Client, message):
    await message.reply("- قفلت آلكول لي لسـه بــدري 🙂")

@Client.on_message(filters.video_chat_members_invited)
async def fuckoff(client: Client, message):
    text = f"آنت يآ  {message.from_user.mention} يا جمـيل\n دعيت للمـكآلمـه : "
    x = 0
    for user in m.video_chat_members_invited.users:
        try:
            text += f"{user.first_name} "
            x += 1
        except Exception:
            pass
    try:
        await m.reply(f"{text} \n**آيوآ بــقآ آديلو 🌚💕️", reply_to_message_id=m.message_id)
    except:
        pass
        
@Client.on_message(filters.command(["عشوائي", "تشغيل عشوائي"], ""))
async def aii(client: Client, message):
   if await joinch(message):
            return
   try:
    chat_id = message.chat.id
    bot_username = client.me.username
    rep = await message.reply_text("**جاري تشغيل اغنية عشوائية لك انتظر قد يستغرق بعض القائق .**")
    try:
          call = await get_call(bot_username)
    except:
          await remove_active(bot_username, chat_id)
    try:
       await call.get_call(message.chat.id)
    except pytgcalls.exceptions.GroupCallNotFound:
       await remove_active(bot_username, chat_id)
    message_id = message.id
    user = await get_userbot(bot_username)
    req = message.from_user.mention if message.from_user else message.chat.title
    raw_list = []
    async for msg in user.get_chat_history("ELNQYBMUSIC"):
        if msg.audio:
          raw_list.append(msg)
    x = random.choice(raw_list)
    file_path = await x.download()
    file_name = x.audio.title
    title = file_name
    dur = x.audio.duration
    duration = seconds_to_min(dur)
    photo = PHOTO
    vid = True if x.video else None
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else "S_E_M_O_E_L_K_B_E_R"
    videoid = None
    link = None
    await add(message.chat.id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
    if not await is_served_call(client, message.chat.id): 
      await add_active_chat(chat_id)
      await add_served_call(client, chat_id)
      if vid:
        await add_active_video_chat(chat_id)
      link = None
      c = await join_call(client, message_id, chat_id, bot_username, file_path, link, vid)
      if not c:
            await remove_active(bot_username, chat_id)
            return await rep.delete()
    await rep.delete()
    gr = await get_group(bot_username)
    ch = await get_channel(bot_username)
    button = [[InlineKeyboardButton(text="ᴇɴᴅ", callback_data=f"stop"), InlineKeyboardButton(text="ʀᴇѕụᴍᴇ", callback_data=f"resume"), InlineKeyboardButton(text="ᴘᴀụѕᴇ", callback_data=f"pause")], [InlineKeyboardButton(text="ᴄʜᴀɴᴇᴇʟ", url=f"{ch}"), InlineKeyboardButton(text="ɢʀᴏụᴘ", url=f"{gr}")], [InlineKeyboardButton(text=f"{OWNER_NAME}", url="https://t.me/{OWNER[0]}")], [InlineKeyboardButton(text="ᴀᴅᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ʏᴏụʀ ɢʀᴏụᴘ ⌯", url=f"https://t.me/{bot_username}?startgroup=True")]]
    await message.reply_photo(photo=photo, caption=f"**ѕᴛᴀʀᴛᴇᴅ ѕᴛʀᴇᴀᴍ ʀᴀɴᴅᴏᴍ **\n\n**ѕᴏɴɢ ɴᴀᴍᴇ : {title}**\n**ᴅụʀᴀᴛɪᴏɴ ᴛɪᴍᴇ : {duration}**\n**ʀᴇǫụᴇѕᴛѕ ʙʏ : {req}**", reply_markup=InlineKeyboardMarkup(button))
    await logs(bot_username, client, message)
    await asyncio.sleep(4)
    os.remove(file_path)
   except Exception as es:
    pass

@Client.on_message(filters.command(["/play", "play", "/vplay", "شغل", "تشغيل", "فيد", "فيديو"], ""))
async def play(client: Client, message):
  if await joinch(message):
            return
  SEMO = message
  bot_username = client.me.username
  chat_id = message.chat.id
  user_id = message.from_user.id if message.from_user else "S_E_M_O_E_L_K_B_E_R"
  message_id = message.id 
  gr = await get_group(bot_username)
  ch = await get_channel(bot_username)
  button = [[InlineKeyboardButton(text="ᴇɴᴅ", callback_data=f"stop"), InlineKeyboardButton(text="ʀᴇѕụᴍᴇ", callback_data=f"resume"), InlineKeyboardButton(text="ᴘᴀụѕᴇ", callback_data=f"pause")], [InlineKeyboardButton(text="ᴄʜᴀɴᴇᴇʟ", url=f"{ch}"), InlineKeyboardButton(text="ɢʀᴏụᴘ", url=f"{gr}")], [InlineKeyboardButton(text=f"{OWNER_NAME}", url=f"https://t.me/{OWNER[0]}")], [InlineKeyboardButton(text="ᴀᴅᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ʏᴏụʀ ɢʀᴏụᴘ ⌯", url=f"https://t.me/{bot_username}?startgroup=True")]]
  if message.chat.type == ChatType.PRIVATE:
       return await message.reply_text("**لا يمكنك التشغيل هنا للأسف **\n** قم بإضافة البوت اللي مجموعتك للتشغيل**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"ᴀᴅᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ʏᴏụʀ ɢʀᴏụᴘ ⌯", url=f"https://t.me/{bot_username}?startgroup=True")]]))
  if message.sender_chat:
     if not message.chat.type == ChatType.CHANNEL:
      return await message.reply_text("**يمكنك التشغيل بحسابك الخاص فقط .**")
  if not len(message.command) == 1:
    rep = await message.reply_text("**جاري التشغيل انتظر قليلا .**")
  try:
          call = await get_call(bot_username)
  except:
          await remove_active(bot_username, chat_id)
  try:
       await call.get_call(message.chat.id)
  except pytgcalls.exceptions.GroupCallNotFound:
       await remove_active(bot_username, chat_id)
  if not message.reply_to_message:
     if len(message.command) == 1:
      if message.chat.type == ChatType.CHANNEL:
        return await message.reply_text("**قم كتابة شيئ لتشغيلة .**")
      try:
       name = await client.ask(message.chat.id, text="**ارسل اسم او رابط الي تريد تشغيله .**", reply_to_message_id=message.id, filters=filters.user(message.from_user.id), timeout=200)
       name = name.text
       rep = await message.reply_text("**جاري التشغيل انتظر قليلا .**")
      except:
       return
     else:
       name = message.text.split(None, 1)[1]
     try:
      results = VideosSearch(name, limit=1)
     except Exception:
      return await rep.edit("**لم يتم العثور علي نتائج .**")
     for result in (await results.next())["result"]:
         title = result["title"]
         duration = result["duration"]
         videoid = result["id"]
         yturl = result["link"]
         thumbnail = result["thumbnails"][0]["url"].split("?")[0]
     if "v" in message.command[0] or "ف" in message.command[0]:
       vid = True
     else:
       vid = None
     await rep.edit("**جاري التشغيل انتظر قليلا  🔄**")
     results = YoutubeSearch(name, max_results=5).to_dict()
     link = f"https://youtube.com{results[0]['url_suffix']}"
     if await is_served_call(client, message.chat.id):
         chat_id = message.chat.id
         title = title.title()
         file_path = None
         await add(message.chat.id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
         chat = f"{bot_username}{chat_id}"
         position = len(db.get(chat)) - 1
         chatname = f"[{message.chat.title}](https://t.me/{message.chat.username})" if message.chat.username else f"{message.chat.title}"
         chatname = f"{message.author_signature}" if message.author_signature else chatname
         requester = chatname if SEMO.views else f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
         if message.from_user:
          if message.from_user.photo:
           photo_id = message.from_user.photo.big_file_id
           photo = await client.download_media(photo_id)
          elif message.chat.photo:
           photo_id = message.chat.photo.big_file_id
           photo = await client.download_media(photo_id)
          else:
           ahmed = await client.get_chat("S_E_M_O_E_L_K_B_E_R")
           ahmedphoto = ahmed.photo.big_file_id
         elif message.chat.photo:
          photo_id = message.chat.photo.big_file_id
          photo = await client.download_media(photo_id)
         else:
          ahmed = await client.get_chat("S_E_M_O_E_L_K_B_E_R")
          ahmedphoto = ahmed.photo.big_file_id
          photo = await client.download_media(ahmedphoto)
         photo = await gen_thumb(videoid, photo)
         await message.reply_photo(photo=photo, caption=f"**ᴀᴅᴅ ᴛʀᴀᴄᴋ ᴛᴏ ᴘʟᴀʏʟɪѕᴛ » {position}**\n\n**ѕᴏɴɢ ɴᴀᴍᴇ : {title[:18]}**\n**ᴅụʀᴀᴛɪᴏɴ ᴛɪᴍᴇ : {duration}**\n**ʀᴇǫụᴇѕᴛѕ ʙʏ : {requester}**", reply_markup=InlineKeyboardMarkup(button))
         await logs(bot_username, client, message)
     else:
         chat_id = message.chat.id
         title = title.title()
         await add_active_chat(chat_id)
         await add_served_call(client, chat_id)
         if vid:
           await add_active_video_chat(chat_id)
         file_path = await download(bot_username, link, vid)
         await add(message.chat.id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
         c = await join_call(client, message_id, chat_id, bot_username, file_path, link, vid)
         if not c:
            await remove_active(bot_username, chat_id)
            return await rep.delete()
         chatname = f"[{message.chat.title}](https://t.me/{message.chat.username})" if message.chat.username else f"{message.chat.title}"
         chatname = f"{message.author_signature}" if message.author_signature else chatname
         requester = chatname if SEMO.views else f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
         if message.from_user:
          if message.from_user.photo:
           photo_id = message.from_user.photo.big_file_id
           photo = await client.download_media(photo_id)
          elif message.chat.photo:
           photo_id = message.chat.photo.big_file_id
           photo = await client.download_media(photo_id)
          else:
           ahmed = await client.get_chat("S_E_M_O_E_L_K_B_E_R")
           ahmedphoto = ahmed.photo.big_file_id
         elif message.chat.photo:
          photo_id = message.chat.photo.big_file_id
          photo = await client.download_media(photo_id)
         else:
          ahmed = await client.get_chat("S_E_M_O_E_L_K_B_E_R")
          ahmedphoto = ahmed.photo.big_file_id
          photo = await client.download_media(ahmedphoto)
         photo = await gen_thumb(videoid, photo)
         await message.reply_photo(photo=photo, caption=f"**ѕᴛᴀʀᴛɪɴɢ ᴘʟᴀʏɪɴɢ ɴᴏᴡ**\n\n**ѕᴏɴɢ ɴᴀᴍᴇ : {title[:18]}**\n**ᴅụʀᴀᴛɪᴏɴ ᴛɪᴍᴇ : {duration}**\n**ʀᴇǫụᴇѕᴛѕ ʙʏ : {requester}**", reply_markup=InlineKeyboardMarkup(button))
         await logs(bot_username, client, message)
     await rep.delete()
  else:
       if not message.reply_to_message.media:
         return
       rep = await message.reply_text("**جاري تشغيل الملف  .**") 
       photo = "Uploaded to https://telegra.ph/file/448774fc5d5a1ea025a5a.jpg"
       if message.reply_to_message.video or message.reply_to_message.document:
           vid = True
       else:
           vid = None
       file_path = await message.reply_to_message.download()
       if message.reply_to_message.audio:
         file_name = message.reply_to_message.audio
       elif message.reply_to_message.voice:
         file_name = message.reply_to_message.voice
       elif message.reply_to_message.video:
         file_name = message.reply_to_message.video
       else:
         file_name = message.reply_to_message.document
       title = file_name.file_name
       duration = seconds_to_min(file_name.duration)
       link = None
       if await is_served_call(client, message.chat.id):
         chat_id = message.chat.id
         videoid = None
         await add(message.chat.id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
         chat = f"{bot_username}{chat_id}"
         position = len(db.get(chat)) - 1
         chatname = f"[{message.chat.title}](https://t.me/{message.chat.username})" if message.chat.username else f"{message.chat.title}"
         chatname = f"{message.author_signature}" if message.author_signature else chatname
         requester = chatname if SEMO.views else f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
         await message.reply_photo(photo=photo, caption=f"**ᴀᴅᴅ ᴛʀᴀᴄᴋ ᴛᴏ ᴘʟᴀʏʟɪѕᴛ » {position}**\n\n**ѕᴏɴɢ ɴᴀᴍᴇ : {title}**\n**ᴅụʀᴀᴛɪᴏɴ ᴛɪᴍᴇ {duration}**\n**ʀᴇǫụᴇѕᴛѕ ʙʏ : {requester}**", reply_markup=InlineKeyboardMarkup(button))
         await logs(bot_username, client, message)
       else:
         chat_id = message.chat.id
         videoid = None
         await add_active_chat(chat_id)
         await add_served_call(client, chat_id)
         if vid:
            await add_active_video_chat(chat_id)
         await add(message.chat.id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
         c = await join_call(client, message_id, chat_id, bot_username, file_path, link, vid)
         if not c:
            await remove_active(bot_username, chat_id)
            return await rep.delete()
         chatname = f"[{message.chat.title}](https://t.me/{message.chat.username})" if message.chat.username else f"{message.chat.title}"
         chatname = f"{message.author_signature}" if message.author_signature else chatname
         requester = chatname if SEMO.views else f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
         await message.reply_photo(photo=photo, caption=f"**ѕᴛᴀʀᴛɪɴɢ ᴘʟᴀʏɪɴɢ ɴᴏᴡ**\n\n**ѕᴏɴɢ ɴᴀᴍᴇ : {title}**\n**ᴅụʀᴀᴛɪᴏɴ ᴛɪᴍᴇ {duration}**\n**ʀᴇǫụᴇѕᴛѕ ʙʏ : {requester}**", reply_markup=InlineKeyboardMarkup(button))
         await logs(bot_username, client, message)
  try:
     os.remove(file_path)
     os.remove(photo)
  except:
     pass
  await rep.delete()


