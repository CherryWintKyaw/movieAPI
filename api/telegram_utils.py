# api/telegram_utils.py
import asyncio
from django.conf import settings
from telethon import TelegramClient
from telethon.sessions import StringSession

api_id = settings.TELEGRAM_API_ID
api_hash = settings.TELEGRAM_API_HASH
bot_token = settings.TELEGRAM_BOT_TOKEN

# Global client ဆောက်မယ် (Session file မသုံးဘဲ StringSession သုံးတာ အကောင်းဆုံးပဲ)
client = TelegramClient(StringSession(), api_id, api_hash)

async def get_video_stream(message_id, channel_id):
    try:
        # Client က Connect မဖြစ်သေးရင် တစ်ကြိမ်ပဲ ချိတ်မယ်
        if not client.is_connected():
            await client.connect()
            
        # Login မဝင်ရသေးရင် Bot Token နဲ့ ဝင်မယ်
        if not await client.is_user_authorized():
            await client.start(bot_token=bot_token)
            
        entity = await client.get_entity(int(channel_id))
        message = await client.get_messages(entity, ids=int(message_id))
        
        if message and message.video:
            async for chunk in client.iter_download(message.video, chunk_size=1024*1024):
                yield chunk
    except Exception as e:
        print(f"Streaming Error: {e}")