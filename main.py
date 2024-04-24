import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import os
import threading
import json
from pyrogram.errors.exceptions.bad_request_400 import MessageEmpty
from pyrogram.types import Message
from subprocess import getstatusoutput

# Load configuration from config.json
with open('config.json', 'r') as f: 
    DATA = json.load(f)

def getenv(var): 
    return os.environ.get(var) or DATA.get(var, None)

bot_token = getenv("TOKEN") 
api_hash = getenv("HASH") 
api_id = getenv("ID")
auth_users = 5374602611
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

ss = getenv("STRING")
if ss is not None:
    acc = Client("myacc" ,api_id=api_id, api_hash=api_hash, session_string=ss)
    acc.start()
else: 
    acc = None

# Define global variables
words_to_remove_from_filename = []
given_thumbnail = "not_set"
url_count = 0
# Default replacements
words_to_replace_in_caption = {}


# download status
def downstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"╭──⌈📥Downloading📥⌋──╮\n├ 𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨 📈-: **{txt}**\n╰────⌈ ʟʊʍɨռǟռȶ ⌋────╯")
            time.sleep(10)
        except:
            time.sleep(5)

# upload status
def upstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"╭──⌈📤 𝙐𝙥𝙡𝙤𝙖𝙙𝙞𝙣𝙜 📤⌋──╮\n├ 𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨 📈: **{txt}**\n╰────⌈ ʟʊʍɨռǟռȶ ⌋────╯")
            time.sleep(10)
        except:
            time.sleep(5)

# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")


# start command
@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    bot.send_message(message.chat.id, "Yes I am Active")

@bot.on_message(filters.command(["replace"]) & filters.chat(-1002115474889))
def replace_command_handler(client, message):
    global words_to_replace_in_caption
    try:
        # Extract the replacement pairs from the command
        replace_data = message.text.split("/replace ")[1]
        # Split the replacement pairs by comma
        replace_pairs = replace_data.split(',')
        replace_dict = {}
        for pair in replace_pairs:
            # Split each pair by colon to separate key and value
            key, value = pair.split(':')
            # Remove leading/trailing whitespaces
            key = key.strip()
            value = value.strip()
            # Add the pair to the replacement dictionary
            replace_dict[key] = value
        # Update the global words_to_replace_in_caption dictionary with the new replacement pairs
        words_to_replace_in_caption.update(replace_dict)
        # Inform the user about the successful update
        bot.send_message(message.chat.id, "Replacement dictionary updated successfully.")
    except:
        bot.send_message(message.chat.id, "Invalid replace command syntax.")

@bot.on_message(filters.command("remove") & filters.chat(-1002115474889))
def handle_remove_command(client: pyrogram.Client, message: pyrogram.types.Message):
    global words_to_remove_from_filename
    # Get the text after the command
    text_after_command = message.text.split(maxsplit=1)[1].strip()
    
    # Check if text is empty
    if not text_after_command:
        bot.send_message(message.chat.id, "Please provide words to remove after the command.")
        return
    
    # Update words to remove from filename
    words_to_remove_from_filename = text_after_command.split(",")
    words_to_remove_from_filename = [word.strip() for word in words_to_remove_from_filename]
    
    # Send a message indicating the set words
    bot.send_message(message.chat.id, f"You have set these words to be removed from the filename and Caption: {', '.join(words_to_remove_from_filename)}")

@bot.on_message((filters.text) & filters.chat(-1002115474889))
def save(client: pyrogram.Client, message: pyrogram.types.Message):
    global given_thumbnail
    print(message.text)

    # joining chats
    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:

        if acc is None:
            bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
            return

        try:
            try: 
                acc.join_chat(message.text)
            except Exception as e: 
                bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)
                return
            bot.send_message(message.chat.id, "**Chat Joined**", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            bot.send_message(message.chat.id, "**Chat alredy Joined**", reply_to_message_id=message.id)
        except InviteHashExpired:
            bot.send_message(message.chat.id, "**Invalid Link**", reply_to_message_id=message.id)

    # getting message
    elif "https://t.me/" in message.text:

        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try: 
            toID = int(temp[1].strip())
        except: 
            toID = fromID

        for msgid in range(fromID, toID+1):

            # private
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])

                if acc is None:
                    bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                    return

                handle_private(message, chatid, msgid)
                # try: handle_private(message,chatid,msgid)
                # except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)

            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]

                if acc is None:
                    bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                    return
                try: 
                    handle_private(message, username, msgid)
                except Exception as e: 
                    bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

            # public
            else:
                username = datas[3]

                try: 
                    msg  = bot.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    bot.send_message(message.chat.id, f"**The username is not occupied by anyone**", reply_to_message_id=message.id)
                    return

                try: 
                    bot.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    if acc is None:
                        bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                        return
                    try: 
                        handle_private(message, username, msgid)
                    except Exception as e: 
                        bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

            # wait time
            time.sleep(3)

    if "https://graph.org" in message.text:
        set_thumb = message.text
        if set_thumb.startswith("http://") or set_thumb.startswith("https://"):
            # Download the image file using wget
            getstatusoutput(f"wget '{set_thumb}' -O 'set_thumb.jpg'")
            given_thumbnail = "set_thumb.jpg"
            # Send a message confirming thumbnail set successfully
            bot.send_message(message.chat.id, "Thumbnail has been set successfully.")
    else:
        given_thumbnail = "not_set"

def handle_private(message: pyrogram.types.messages_and_media.message.Message, chatid: int, msgid: int):
    global given_thumbnail, words_to_remove_from_filename, url_count
    global words_to_replace_in_caption
    
    try:
        msg: pyrogram.types.messages_and_media.message.Message = acc.get_messages(chatid, msgid)
        msg_type = get_message_type(msg)

        if given_thumbnail != "not_set":
            thumb = given_thumbnail
        else:
            thumb = "https://graph.org/file/818aa312b35052a5c4d74.jpg"
            getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
            thumb = "thumb.jpg"

        modified_filename = None  # Initialize modified_filename variable

        if "Text" == msg_type:
            bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
            return

        smsg = bot.send_message(message.chat.id, '__Downloading__', reply_to_message_id=message.id)
        dosta = threading.Thread(target=lambda: downstatus(f'{message.id}downstatus.txt', smsg), daemon=True)
        dosta.start()
        file = acc.download_media(msg, progress=progress, progress_args=[message, "down"])
        os.remove(f'{message.id}downstatus.txt')

        upsta = threading.Thread(target=lambda: upstatus(f'{message.id}upstatus.txt', smsg), daemon=True)
        upsta.start()

        # Modify the file name before sending
        filename, file_extension = os.path.splitext(file)
        modified_filename = f"{filename}ʟʊʍɨռǟռȶ{file_extension}"

        # Remove specific words from the file name
        words_to_remove = words_to_remove_from_filename  # Add the words you want to remove
        for word in words_to_remove:
            modified_filename = modified_filename.replace(word, "")

        os.rename(file, modified_filename)
        
        # Replace specific words in the caption
        caption = msg.caption if msg.caption else ""
        for word, replacement in words_to_replace_in_caption.items():
            caption = caption.replace(word, replacement)

        # Remove specific words from the caption
        for word in words_to_remove_from_filename:
            caption = caption.replace(word, "")

        # Set URL count limit based on media type
        if "Document" == msg_type or "Photo" == msg_type or "Audio" == msg_type:
            url_limit = 10
        elif "Video" == msg_type:
            url_limit = 50

        # Increment URL count
        url_count += 1
        # Check if URL count is divisible by the limit
        if url_count % url_limit == 0:
            # Initiate flood wait (5 minutes)
            time.sleep(300)

        # Send the media
        if "Document" == msg_type:
            bot.send_document(message.chat.id, modified_filename, thumb=thumb, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        elif "Video" == msg_type:
            bot.send_video(message.chat.id, modified_filename, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        elif "Audio" == msg_type:
            bot.send_audio(message.chat.id, modified_filename, duration=msg.audio.duration, performer=msg.audio.performer, title=msg.audio.title, thumb=thumb, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        elif "Photo" == msg_type:
            bot.send_photo(message.chat.id, modified_filename, thumb=thumb, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        # Add more elif conditions for other message types here...

        # Cleanup
        if os.path.exists(file):  # Check if the original file exists before removal
            os.remove(file)  # Remove the original file
        if modified_filename and os.path.exists(modified_filename):
            os.remove(modified_filename)  # Remove the modified file if it exists
        if os.path.exists(f'{message.id}upstatus.txt'):
            os.remove(f'{message.id}upstatus.txt')
        bot.delete_messages(message.chat.id, [smsg.id])
        
    except pyrogram.errors.exceptions.bad_request_400.MessageEmpty:
        # Skip to the next iteration if the message is empty
        pass


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
	try:
		msg.document.file_id
		return "Document"
	except: pass

	try:
		msg.video.file_id
		return "Video"
	except: pass

	try:
		msg.animation.file_id
		return "Animation"
	except: pass

	try:
		msg.sticker.file_id
		return "Sticker"
	except: pass

	try:
		msg.voice.file_id
		return "Voice"
	except: pass

	try:
		msg.audio.file_id
		return "Audio"
	except: pass

	try:
		msg.photo.file_id
		return "Photo"
	except: pass

	try:
		msg.text
		return "Text"
	except: pass

# infinty polling
bot.run()
