from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InputMediaDocument, Message, InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image
from datetime import datetime
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.utils import progress_for_pyrogram, humanbytes, convert
from helper.database import madflixbotz
from config import Config
import os
import time
import re
import asyncio

# Function to update metadata for videos
def update_video_metadata(input_file, output_file, title, subtitle):
    import ffmpeg
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, metadata=f"title={title}", metadata=f"comment={subtitle}")
            .run(overwrite_output=True)
        )
        return output_file
    except Exception as e:
        print(f"Error updating video metadata: {e}")
        return input_file  # Return original file if metadata update fails

# Function to update metadata for audio files
def update_audio_metadata(input_file, title, artist, album):
    import mutagen
    from mutagen.easyid3 import EasyID3
    try:
        audio = EasyID3(input_file)
        audio['title'] = title
        audio['artist'] = artist
        audio['album'] = album
        audio.save()
        return input_file
    except Exception as e:
        print(f"Error updating audio metadata: {e}")
        return input_file

# Extract metadata from file
def extract_file_metadata(file_path):
    metadata = extractMetadata(createParser(file_path))
    if metadata:
        title = metadata.get("title", "Unknown Title")
        artist = metadata.get("artist", "Unknown Artist")
        album = metadata.get("album", "Unknown Album")
        return title, artist, album
    return "Unknown Title", "Unknown Artist", "Unknown Album"

# Handler for rename command with metadata buttons
@Client.on_message(filters.command("rename") & filters.private)
async def rename_file(client, message):
    new_name = "NewFile.mp4"  # Example new name
    file_path = "downloads/input.mp4"
    output_file = "downloads/output.mp4"

    buttons = [
        [InlineKeyboardButton("✅ Apply Metadata", callback_data="apply_metadata")],
        [InlineKeyboardButton("❌ Skip Metadata", callback_data="skip_metadata")]
    ]
    await message.reply_text("Do you want to update metadata?", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("apply_metadata"))
async def apply_metadata_handler(client, query):
    file_path = "downloads/input.mp4"
    ext = os.path.splitext(file_path)[1].lower()
    output_file = "downloads/output.mp4"

    title, artist, album = extract_file_metadata(file_path)

    if ext in [".mp3", ".m4a", ".flac"]:
        updated_file = update_audio_metadata(file_path, title, artist, album)
    elif ext in [".mp4", ".mkv"]:
        updated_file = update_video_metadata(file_path, output_file, title, "Auto Subtitle")

    await query.message.reply_document(updated_file, caption="Metadata updated & file renamed!")

@Client.on_callback_query(filters.regex("skip_metadata"))
async def skip_metadata_handler(client, query):
    await query.message.reply_text("Metadata update skipped. File renamed only.")
