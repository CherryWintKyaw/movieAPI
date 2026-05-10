import os
from django.conf import settings
from telethon import TelegramClient
from telethon.sessions import StringSession

api_id = settings.TELEGRAM_API_ID
api_hash = settings.TELEGRAM_API_HASH
bot_token = settings.TELEGRAM_BOT_TOKEN

# StringSession() က database file မဆောက်ဘဲ memory ထဲမှာပဲ အလုပ်လုပ်လို့ Lock မဖြစ်တော့ပါဘူး
client = TelegramClient(StringSession(), api_id, api_hash)

async def get_video_stream(message_id, channel_id):
    # Connection စစ်ဆေးခြင်း
    if not client.is_connected():
        await client.start(bot_token=bot_token)
    
    try:
        # Channel entity ကို ယူခြင်း
        entity = await client.get_entity(int(channel_id))
        # Message ကို ယူခြင်း
        message = await client.get_messages(entity, ids=int(message_id))
        
        if message and message.video:
            # Video ကို chunk လိုက် yield လုပ်ပေးခြင်း
            async for chunk in client.iter_download(message.video, chunk_size=1024*1024):
                yield chunk
    except Exception as e:
        print(f"Streaming Error in Utils: {e}")