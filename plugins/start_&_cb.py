import random
from pyrogram.types import ForceReply
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message

from helper.database import madflixbotz
from config import Config, Txt  

@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    await madflixbotz.add_user(client, message)                
    button = InlineKeyboardMarkup([[
      InlineKeyboardButton('📢 Updates', url='https://t.me/animelibraryn4')
    ],[
      InlineKeyboardButton('⚙️ Help', callback_data='help'),
      InlineKeyboardButton('🙂 About', callback_data='about')
    ]])
    if Config.START_PIC:
        await message.reply_photo(Config.START_PIC, caption=Txt.START_TXT.format(user.mention), reply_markup=button)       
    else:
        await message.reply_text(text=Txt.START_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)   

@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data 
    user_id = query.from_user.id  
    
    if data == "home":
        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton('📢 Updates', url='https://t.me/animelibraryn4')
                ],[
                InlineKeyboardButton('⚙️ Help', callback_data='help'),
                InlineKeyboardButton('🙂 About', callback_data='about')
                ]])
        )

    elif data == "metadata":
        metadata_info = await madflixbotz.get_metadata(user_id)
        file_name = await madflixbotz.get_file_name(user_id)

        metadata_text = f"**📜 Current Metadata:**\n{metadata_info}" if metadata_info else "❌ No Metadata Set."
        file_name_text = f"**📁 File Name:** `{file_name}`" if file_name else "❌ No File Name Set."
        
        await query.message.edit_text(
            text=f"{metadata_text}\n\n{file_name_text}",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✏️ Set Metadata", callback_data="set_metadata"),
                InlineKeyboardButton("✖️ Close", callback_data="close")
            ]])          
        )

    elif data == "set_metadata":
        await query.message.reply_text(
            "Send the metadata and file name you want to set in the format:\n\n"
            "`file_name: your_file_name.mp4`\n"
            "`title: XYZ`\n"
            "`artist: ABC`\n"
            "`year: 2023`",
            reply_markup=ForceReply(selective=True)
        )
    
    elif data == "close":
        try:
            await query.message.delete()
        except:
            pass

# --- NEW: `/metadata` Command ---
@Client.on_message(filters.private & filters.command("metadata"))
async def metadata_command(client, message: Message):
    user_id = message.from_user.id
    metadata = await madflixbotz.get_metadata(user_id)
    file_name = await madflixbotz.get_file_name(user_id)

    metadata_text = f"**📜 Current Metadata:**\n{metadata}" if metadata else "❌ No Metadata Set."
    file_name_text = f"**📁 File Name:** `{file_name}`" if file_name else "❌ No File Name Set."
    
    await message.reply_text(f"{metadata_text}\n\n{file_name_text}")

# --- NEW: Handle Metadata & File Name ---
@Client.on_message(filters.private & filters.reply)
async def handle_metadata(client, message: Message):
    user_id = message.from_user.id
    if message.reply_to_message and "Send the metadata and file name" in message.reply_to_message.text:
        metadata_text = message.text.strip()
        
        # Extract file name if provided
        file_name = None
        lines = metadata_text.split("\n")
        new_metadata = []
        
        for line in lines:
            if line.startswith("file_name:"):
                file_name = line.split(":", 1)[1].strip()
            else:
                new_metadata.append(line)

        # Store metadata and file name
        await madflixbotz.set_metadata(user_id, "\n".join(new_metadata))
        if file_name:
            await madflixbotz.set_file_name(user_id, file_name)
        
        # Confirmation Message
        confirmation_text = "**✅ Metadata Successfully Updated!**\n\n"
        confirmation_text += f"**📁 File Name:** `{file_name}`\n" if file_name else ""
        confirmation_text += f"**📜 Metadata:**\n{metadata_text}"

        await message.reply_text(confirmation_text)
