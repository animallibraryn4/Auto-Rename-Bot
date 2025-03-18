import random
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
    elif data == "caption":
        await query.message.edit_text(
            text=Txt.CAPTION_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖️ Close", callback_data="close"),
                InlineKeyboardButton("🔙 Back", callback_data="help")
            ]])            
        )
    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT.format(client.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⚙️ Setup AutoRename Format ⚙️", callback_data='file_names')
                ],[
                InlineKeyboardButton('🖼️ Thumbnail', callback_data='thumbnail'),
                InlineKeyboardButton('✏️ Caption', callback_data='caption')
                ],[
                InlineKeyboardButton('📑 Metadata', callback_data='metadata'),  # Added Metadata Button
                InlineKeyboardButton('🏠 Home', callback_data='home'),
                InlineKeyboardButton('💰 Donate', callback_data='donate')
                ]])
        )
    elif data == "donate":
        await query.message.edit_text(
            text=Txt.DONATE_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖️ Close", callback_data="close"),
                InlineKeyboardButton("🔙 Back", callback_data="help")
            ]])          
        )
    
    elif data == "file_names":
        format_template = await madflixbotz.get_format_template(user_id)
        await query.message.edit_text(
            text=Txt.FILE_NAME_TXT.format(format_template=format_template),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖️ Close", callback_data="close"),
                InlineKeyboardButton("🔙 Back", callback_data="help")
            ]])
        )      
    
    elif data == "thumbnail":
        await query.message.edit_caption(
            caption=Txt.THUMBNAIL_TXT,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖️ Close", callback_data="close"),
                InlineKeyboardButton("🔙 Back", callback_data="help"),
            ]]),
        )

    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖️ Close", callback_data="close"),
                InlineKeyboardButton("🔙 Back", callback_data="home")
            ]])          
        )
    
    # NEW: Metadata Handling
    elif data == "metadata":
        metadata_info = await madflixbotz.get_metadata(user_id)
        metadata_text = f"**Current Metadata Settings:**\n{metadata_info}" if metadata_info else "No Metadata Set."
        await query.message.edit_text(
            text=metadata_text,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✏️ Set Metadata", callback_data="set_metadata"),
                InlineKeyboardButton("✖️ Close", callback_data="close")
            ]])          
        )

    elif data == "set_metadata":
        await query.message.reply_text("Send the metadata you want to set in the format:\n\n`title: XYZ\nartist: ABC\nyear: 2023`", reply_markup=ForceReply(selective=True))
    
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            await query.message.delete()
            await query.message.continue_propagation()

# Handler for setting metadata
@Client.on_message(filters.private & filters.reply)
async def handle_metadata(client, message: Message):
    user_id = message.from_user.id
    if message.reply_to_message and "Send the metadata you want to set" in message.reply_to_message.text:
        metadata_text = message.text.strip()
        await madflixbotz.set_metadata(user_id, metadata_text)
        await message.reply_text(f"Metadata Updated:\n\n{metadata_text}")
