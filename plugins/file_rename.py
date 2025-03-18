from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
import os
import asyncio
import re
from datetime import datetime
from helper.utils import progress_for_pyrogram, humanbytes, convert
from helper.database import madflixbotz
from config import Config

# Queue to manage file processing
file_processing_queue = asyncio.Queue()
renaming_operations = {}

# Define metadata update function
def update_audio_metadata(file_path, title, artist="Unknown Artist", album="Unknown Album"):
    try:
        audio = MP3(file_path, ID3=EasyID3)
        audio["title"] = title
        audio["artist"] = artist
        audio["album"] = album
        audio.save()
        return file_path
    except Exception as e:
        print(f"Audio Metadata Update Failed: {e}")
        return file_path

def update_video_metadata(file_path, output_file, title, subtitle=""):
    try:
        video = MP4(file_path)
        video["\xa9nam"] = title
        video["\xa9cmt"] = subtitle
        video.save(output_file)
        return output_file
    except Exception as e:
        print(f"Video Metadata Update Failed: {e}")
        return file_path

# Handler for file uploads
@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def enqueue_file_for_processing(client, message):
    await file_processing_queue.put((client, message))

async def process_file_processing_queue():
    while True:
        client, message = await file_processing_queue.get()
        try:
            await auto_rename_files(client, message)
        except Exception as e:
            print(f"Error processing file: {e}")
        finally:
            file_processing_queue.task_done()

async def auto_rename_files(client, message):
    user_id = message.from_user.id
    format_template = await madflixbotz.get_format_template(user_id)
    media_preference = await madflixbotz.get_media_preference(user_id)

    if not format_template:
        return await message.reply_text("Please Set An Auto Rename Format First Using /autorename")

    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        media_type = media_preference or "document"
    elif message.video:
        file_id = message.video.file_id
        file_name = f"{message.video.file_name}.mp4"
        media_type = media_preference or "video"
    elif message.audio:
        file_id = message.audio.file_id
        file_name = f"{message.audio.file_name}.mp3"
        media_type = media_preference or "audio"
    else:
        return await message.reply_text("Unsupported File Type")

    print(f"Original File Name: {file_name}")
    
    if file_id in renaming_operations:
        elapsed_time = (datetime.now() - renaming_operations[file_id]).seconds
        if elapsed_time < 10:
            return

    renaming_operations[file_id] = datetime.now()
    
    _, file_extension = os.path.splitext(file_name)
    new_file_name = f"{format_template}{file_extension}"
    file_path = f"downloads/{new_file_name}"

    download_msg = await message.reply_text("Trying To Download.....")
    try:
        path = await client.download_media(message=file_path, progress=progress_for_pyrogram, progress_args=("Downloading...", download_msg, time.time()))
    except Exception as e:
        del renaming_operations[file_id]
        return await download_msg.edit(e)

    duration = 0
    try:
        metadata = extractMetadata(createParser(file_path))
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
    except Exception as e:
        print(f"Error getting duration: {e}")

    # **Ask User If They Want to Update Metadata**
    buttons = [
        [InlineKeyboardButton("✅ Yes, Update Metadata", callback_data=f"update_metadata:{file_path}:{media_type}")],
        [InlineKeyboardButton("❌ No, Skip Metadata", callback_data=f"skip_metadata:{file_path}:{media_type}")]
    ]
    await message.reply_text("Do you want to update metadata for this file?", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("update_metadata"))
async def update_metadata_handler(client, query):
    _, file_path, media_type = query.data.split(":")
    
    new_title = os.path.basename(file_path).split('.')[0]  # Extract filename as title
    
    if media_type == "audio":
        updated_file = update_audio_metadata(file_path, new_title, "Auto Artist", "Auto Album")
    elif media_type == "video":
        updated_file = update_video_metadata(file_path, file_path, new_title, "Auto Subtitle")
    
    await query.message.reply_text("Metadata updated! Uploading file now...")
    await send_updated_file(client, query.message.chat.id, updated_file, media_type)

@Client.on_callback_query(filters.regex("skip_metadata"))
async def skip_metadata_handler(client, query):
    _, file_path, media_type = query.data.split(":")
    await query.message.reply_text("Skipping metadata update. Uploading file now...")
    await send_updated_file(client, query.message.chat.id, file_path, media_type)

async def send_updated_file(client, chat_id, file_path, media_type):
    caption = f"**{os.path.basename(file_path)}**"
    
    if media_type == "document":
        await client.send_document(chat_id, document=file_path, caption=caption)
    elif media_type == "video":
        await client.send_video(chat_id, video=file_path, caption=caption)
    elif media_type == "audio":
        await client.send_audio(chat_id, audio=file_path, caption=caption)
    
    os.remove(file_path)

# Start processing queue
async def start_file_processing_queue():
    await process_file_processing_queue()

app = Client("my_bot")
async def main():
    asyncio.create_task(start_file_processing_queue())
    await app.start()
    await idle()

if __name__ == "__main__":
    asyncio.run(main()) if not asyncio.get_event_loop().is_running() else asyncio.create_task(main())
