from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from helper.utils import progress_for_pyrogram
from helper.database import madflixbotz
import os
import time
import re

renaming_queue = []
processing = False  # Flag to indicate if a file is being processed

# Patterns to extract episode number
pattern1 = re.compile(r'S(\d+)(?:E|EP)(\d+)', re.IGNORECASE)
pattern2 = re.compile(r'E(\d+)', re.IGNORECASE)  # Finds "E07" or "EP07"
pattern3 = re.compile(r'(\d{1,2})$', re.IGNORECASE)  # Finds last numbers if no clear season/episode format

# Patterns to extract quality
quality_pattern1 = re.compile(r'\b(\d{3,4}p)\b', re.IGNORECASE)  # Finds "1080p" "720p"
quality_pattern2 = re.compile(r'\b(4k|2k|HdRip)\b', re.IGNORECASE)  # Finds "4K", "2K", "HDRip"

def extract_episode_number(filename):
    for pattern in [pattern1, pattern2, pattern3]:
        match = re.search(pattern, filename)
        if match:
            return match.group(1) if len(match.groups()) == 1 else match.group(2)
    return None  # Return None if no episode number is found

def extract_quality(filename):
    for pattern in [quality_pattern1, quality_pattern2]:
        match = re.search(pattern, filename)
        if match:
            return match.group(1)
    return "Unknown"  # Return "Unknown" if no quality is found

async def process_rename_queue(client):
    global processing
    if processing or not renaming_queue:
        return
    
    processing = True
    while renaming_queue:
        message = renaming_queue.pop(0)
        await rename_file(client, message)
    processing = False

async def rename_file(client, message):
    user_id = message.from_user.id
    format_template = await madflixbotz.get_format_template(user_id)
    media_preference = await madflixbotz.get_media_preference(user_id)

    if not format_template:
        return await message.reply_text("Please set an auto-rename format using /autorename")

    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        media_type = media_preference or "document"
    elif message.video:
        file_id = message.video.file_id
        file_name = f"{message.video.file_name}.mp4"
        media_type = media_preference or "video"
    else:
        return await message.reply_text("Unsupported file type")

    # Extract episode number and quality
    episode_number = extract_episode_number(file_name)
    quality = extract_quality(file_name)

    # Replace placeholders in the format
    if episode_number:
        format_template = format_template.replace("{episode}", str(episode_number))
    if quality != "Unknown":
        format_template = format_template.replace("{quality}", quality)

    # Construct new file name
    _, file_extension = os.path.splitext(file_name)
    new_file_name = f"{format_template}{file_extension}"
    file_path = f"downloads/{new_file_name}"

    download_msg = await message.reply_text("Downloading...")
    try:
        path = await client.download_media(
            message, file_name=file_path, 
            progress=progress_for_pyrogram, 
            progress_args=("Download started...", download_msg, time.time())
        )
    except Exception as e:
        return await download_msg.edit(f"Download failed: {e}")
    
    upload_msg = await download_msg.edit("Uploading...")
    try:
        await client.send_document(
            message.chat.id, 
            document=file_path, 
            caption=f"**{new_file_name}**"
        )
    except Exception as e:
        return await upload_msg.edit(f"Upload failed: {e}")

    os.remove(file_path)
    await upload_msg.delete()

@Client.on_message(filters.private & (filters.document | filters.video))
async def queue_rename(client, message):
    renaming_queue.append(message)
    await process_rename_queue(client)
