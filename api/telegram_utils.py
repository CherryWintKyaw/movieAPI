import asyncio
from telethon import TelegramClient
from django.conf import settings
import os

# Settings ထဲက data များကို ယူသည်
API_ID = settings.TELEGRAM_API_ID
API_HASH = settings.TELEGRAM_API_HASH
# Session ဖိုင်ကို project root ထဲမှာ သိမ်းဆည်းရန်
SESSION_PATH = os.path.join(settings.BASE_DIR, 'popcorn_session')

# Client ကို တစ်ကြိမ်ပဲ initialize လုပ်သည်
client = TelegramClient(SESSION_PATH, API_ID, API_HASH)

async def get_video_stream(message_id, channel_id):
    # Client connection ကို စစ်ဆေးသည်
    if not client.is_connected():
        await client.connect()

    try:
        # Channel ID format ကို handle လုပ်သည်
        c_id = str(channel_id)
        if not c_id.startswith('-100'):
            entity_id = int(f"-100{c_id}")
        else:
            entity_id = int(c_id)

        # Message object ကို ယူသည်
        entity = await client.get_entity(entity_id)
        message = await client.get_messages(entity, ids=int(message_id))
        
        if message and message.video:
            # ဗီဒီယို chunk များကို generator အနေဖြင့် ထုတ်ပေးသည်
            async for chunk in client.iter_download(message.video):
                yield chunk
        else:
            print("Error: Video not found in the specified message.")
            yield b""

    except Exception as e:
        print(f"Telegram Utility Error: {str(e)}")
        yield b""