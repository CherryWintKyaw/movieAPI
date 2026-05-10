import os
from django.conf import settings
from telethon import TelegramClient

# settings.py ထဲက data တွေကို လှမ်းယူမယ်
api_id = settings.TELEGRAM_API_ID
api_hash = settings.TELEGRAM_API_HASH
bot_token = settings.TELEGRAM_BOT_TOKEN

# Project root ထဲမှာ 'bot_session' ဆိုပြီး session file တစ်ခု ထွက်လာပါလိမ့်မယ်
client = TelegramClient('bot_session', api_id, api_hash)

async def get_video_stream(message_id, channel_id):
    # Bot connection မရှိသေးရင် ချိတ်မယ်
    if not client.is_connected():
        await client.start(bot_token=bot_token)
    
    try:
        # Channel ထဲက Message ကို ရှာမယ်
        entity = await client.get_entity(int(channel_id))
        message = await client.get_messages(entity, ids=int(message_id))
        
        if message and message.video:
            # Video ကို 1MB အပိုင်းလိုက် (Chunks) ခွဲပြီး User ဆီ ပို့ပေးမယ်
            async for chunk in client.iter_download(message.video, chunk_size=1024*1024):
                yield chunk
    except Exception as e:
        print(f"Streaming Error: {e}")