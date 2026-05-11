import asyncio
from telethon import TelegramClient
from django.conf import settings
import os

API_ID = settings.TELEGRAM_API_ID
API_HASH = settings.TELEGRAM_API_HASH
SESSION_PATH = os.path.join(settings.BASE_DIR, 'popcorn_session')

# client ကို ဒီမှာပဲ initialize လုပ်ထားပါ
client = TelegramClient(SESSION_PATH, API_ID, API_HASH)

async def get_video_stream(message_id, channel_id):
    if not client.is_connected():
        await client.connect()

    try:
        c_id = str(channel_id)
        entity_id = int(f"-100{c_id}") if not c_id.startswith('-100') else int(c_id)
        
        entity = await client.get_entity(entity_id)
        message = await client.get_messages(entity, ids=int(message_id))
        
        if message and message.video:
            # ဗီဒီယိုကို chunk အလိုက် ပို့ပေးတဲ့အခါ buffering error မတက်အောင် sleep လေး ထည့်ပေးပါ
            async for chunk in client.iter_download(message.video, chunk_size=1024*1024): # 1MB chunks
                yield chunk
                await asyncio.sleep(0.01) 
        else:
            yield b""
    except Exception as e:
        print(f"Telegram Error: {e}")
        yield b""