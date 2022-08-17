import asyncio
import shlex
import os
from sys import stderr, stdout
from subprocess import call, check_output
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup


api_id = int(os.environ.get('API_ID', None))
api_hash = os.environ.get('API_HASH', None)
bot_token = os.environ.get('BOT_TOKEN', None)

app = Client(
    "Download:4u",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

if not os.path.isdir('DOWNLOADS'):
    os.makedirs('DOWNLOADS')

  # Getting Video duration & other meta data for the video
def get_duration(filepath):
    metadata = extractMetadata(createParser(filepath))
    if metadata.has("duration"):
        return metadata.get('duration').seconds
    else:
      	return 0

def get_width_height(filepath):
    metadata = extractMetadata(createParser(filepath))
    if metadata.has("width") and metadata.has("height"):
        return metadata.get("width"), metadata.get("height")
    else:
      	return 1280, 720


      
# Download Function
async def command_run(cmd: str):
    args = shlex.split(cmd)
    print(args)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )

@app.on_message(filters.private & filters.command(['start']))
async def start_handler(c:Client, m:Message):
    await m.reply_text(
        text=f"**Hi** {m.from_user.mention}**! Welcome !\nPress /help for more info.**",
        reply_markup=InlineKeyboardMarkup([
          [
            InlineKeyboardButton(text="Settings", callback_data="settings") ,
            InlineKeyboardButton(text="Help", callback_data="help")
          ]
        ]),
        quote=True
    )

@app.on_message(filters.private & filters.command(['help']))
async def help_handler(c:Client, m:Message):
    await m.reply_text(f"Hey {m.from_user.mention} Help Menu", quote=True)

@app.on_message(filters.private & filters.command(['settings']))
async def settings_handler(c:Client, m:Message):
    await m.reply_text(f"Hey {m.from_user.mention} Settings Menu", quote=True)

@app.on_message(filters.private & filters.text)
async def text_handler(c:Client, m:Message):
    download_u = m.text
    if download_u:
        try:
            custom_name_dir = download_u.split("/")[-1].split('.')[0]
            if "herokuapp" in download_u:
                msg = await m.reply_text("**Downloading!**", quote=True)
                if "|" in download_u:
                    url_parts = download_u.split("|")
                    download_link = url_parts[0]
                    print(download_link)
                    custom_name = url_parts[1]
                    download_location = 'DOWNLOADS' + '/' + f'{custom_name_dir}.mp4'
                    print(download_location)
                    await msg.edit("**Downloading to My Server Please wait!**")
                    cmd = f"youtube-dl -c -f 0 --hls-prefer-ffmpeg {download_link} -o {download_location} --no-warnings"
                    await command_run(cmd)
                    await msg.edit("**Getting Video Details!**")
                    width, height = get_width_height(download_location)
                    duration = get_duration(download_location)
                    await msg.edit("**Uploading!**")
                    await c.send_video(m.chat.id, download_location, caption=f"**{custom_name}**", duration=duration, height=height, width=width, supports_streaming=True)
                    os.remove(download_location)
                else:
                    custom_name = download_u.split("/")[-1].split('.')[0]
                    download_location = 'DOWNLOADS' + '/' + f'{custom_name_dir}.mp4'
                    print(download_location)
                        # Downloading Videos Function
                    await msg.edit("**Downloading to My Server Please wait!**")
                    cmd = f"youtube-dl -c -f 0 --hls-prefer-ffmpeg {download_u} -o {download_location} --no-warnings"
                    await command_run(cmd)
                    # Getting video details
                    await msg.edit("**Getting Video Details!**")
                    width, height = get_width_height(download_location)
                    duration = get_duration(download_location)
                    await msg.edit("**Uploading!**")
                    await c.send_video(m.chat.id, download_location, caption=f"**{custom_name}**", duration=duration, height=height, width=width, supports_streaming=True)
                    os.remove(download_location)
            else:
                await m.reply_text("**Invalid Link!**", quote=True)
        except Exception as e:
            print(f'{e}')
print("Start")
app.run()
