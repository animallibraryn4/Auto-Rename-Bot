import re, os, time
id_pattern = re.compile(r'^.\d+$') 

class Config(object):
    # pyro client config
    API_ID    = os.environ.get("API_ID", "22299340")
    API_HASH  = os.environ.get("API_HASH", "09b09f3e2ff1306da4a19888f614d937")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7678362707:AAFOOo8ilAPKPn473A0kzIsM-XyLDfFJSLs") 

    # database config
    DB_NAME = os.environ.get("DB_NAME","madflixbotz")     
    DB_URL  = os.environ.get("DB_URL","mongodb+srv://n4animeedit:u80hdwhlka5NBFfY@cluster0.jowvb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
 
    # other configs
    BOT_UPTIME  = time.time()
    START_PIC   = os.environ.get("START_PIC", "https://4kwallpapers.com/minimal/luffy-straw-hat-20824.html")
    ADMIN       = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '5380609667').split()]
    FORCE_SUB   = os.environ.get("FORCE_SUB", "animelibraryn4") 
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001896877147"))
    
    # wes response configuration     
    WEBHOOK = bool(os.environ.get("WEBHOOK", "True"))


class Txt(object):
    # part of text configuration
        
    START_TXT = """✨Hello {} 
    
🚀 Features:
✅ Auto Rename Files
✅ Custom Thumbnail & Caption
✅ Easy-to-Use Commands

💡 Use /tutorial to get started!

<b>🤖 Powered by @animelibraryn4</b>"""
    
    FILE_NAME_TXT = """<b><u>SETUP AUTO RENAME FORMAT</u></b>

Use These Keywords To Setup Custom File Name

✓ episode :- To Replace Episode Number
✓ quality :- To Replace Video Resolution

📁 ᴜsᴇ /setmedia Video ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴀs ᴀ ᴠɪᴅᴇᴏ.   
📄 ᴜsᴇ /setmedia Document ᴜᴘʟᴏᴀᴅ ᴀs ᴀ ᴅᴏᴄᴜᴍᴇɴᴛ.

<b>➻ Example :</b> <code> /autorename [S01Eepisode][quality] Naruto Shippuden [Dual Audio] @animelibraryn4 @onlyfans_n4 </code>

<b>➻ Your Current Auto Rename Format :</b> <code>{format_template}</code> """
    
    ABOUT_TXT = f"""<b>🤖 Auto Rename Bot:</b> <a href='https://t.me/animelibraryn4'>1 Piece</a>
<b>📝 Language :</b> <a href='https://python.org'>Python 3</a>
<b>📚 Library :</b> <a href='https://pyrogram.org'>Pyrogram 2.0</a>
<b>🚀 Server :</b> <a href='https://heroku.com'>Heroku</a>
<b>📢 Channel :</b> <a href='https://t.me/animelibraryn4'>Anime Library N4</a>
<b>🧑‍💻 Developer :</b> <a href='https://t.me/Tanjiro_kamado_n4_bot'>Anime Library N4</a>"""

    
    THUMBNAIL_TXT = """<b><u>🖼️  HOW TO SET THUMBNAIL</u></b>
    
⦿ You Can Add Custom Thumbnail Simply By Sending A Photo To Me....
    
⦿ /viewthumb - Use This Command To See Your Thumbnail
⦿ /delthumb - Use This Command To Delete Your Thumbnail"""

    CAPTION_TXT = """<b><u>📝  HOW TO SET CAPTION</u></b>
    
⦿ /set_caption - Use This Command To Set Your Caption
⦿ /see_caption - Use This Command To See Your Caption
⦿ /del_caption - Use This Command To Delete Your Caption"""

    PROGRESS_BAR = """\n
<b>📁 Size</b> : {1} | {2}
<b>⏳️ Done</b> : {0}%
<b>🚀 Speed</b> : {3}/s
<b>⏰️ ETA</b> : {4} """
    
    
    DONATE_TXT = """<b>🥲 Thanks For Showing Interest In Donation! ❤️</b>
    
If You Like My Bots & Projects, You Can 🎁 Donate Me Any Amount From 10 Rs Upto Your Choice.
    
<b>🛍 UPI ID:</b> <code>@</code> """
    
    HELP_TXT = """<b>Hey</b> {}
    
Here Is The Help For My Commands."""





