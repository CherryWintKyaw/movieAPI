import asyncio
from telethon import TelegramClient
from django.conf import settings

# 🚩 သင့်ရဲ့ Telegram API Credentials များကို ဒီမှာထည့်ပါ
API_ID = 'YOUR_API_ID' 
API_HASH = 'YOUR_API_HASH'
SESSION_NAME = 'popcorn_session'

# Client ကို Global အနေနဲ့ ကြေညာထားမယ်
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def get_video_stream(message_id, channel_id):
    # ၁။ Client connection ကို စစ်ဆေးပြီး မပွင့်သေးရင် ပွင့်အောင်လုပ်မယ်
    if not client.is_connected():
        await client.connect()

    try:
        # ၂။ Channel ID format ကို မှန်အောင်ပြင်မယ်
        c_id = str(channel_id)
        if not c_id.startswith('-100'):
            entity_id = int(f"-100{c_id}")
        else:
            entity_id = int(c_id)

        # ၃။ Message ကို လှမ်းယူမယ်
        entity = await client.get_entity(entity_id)
        message = await client.get_messages(entity, ids=int(message_id))
        
        if message and message.video:
            # ၄။ Data chunks များကို ပို့ပေးမယ်
            async for chunk in client.iter_download(message.video):
                yield chunk
        else:
            # ဗီဒီယို မရှိရင် empty byte ပြန်မယ် (Unicode Error ကင်းအောင် emoji ဖြုတ်ထားသည်)
            print("Error: Video not found in message")
            yield b""

    except Exception as e:
        # Emoji မပါဘဲ Log ထုတ်မယ်
        print(f"Telegram Utility Error: {str(e)}")
        yield b""