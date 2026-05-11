from telethon import TelegramClient
from telethon.sessions import StringSession
from django.conf import settings

api_id = settings.TELEGRAM_API_ID
api_hash = settings.TELEGRAM_API_HASH
bot_token = settings.TELEGRAM_BOT_TOKEN

# StringSession() ကို သုံးခြင်းဖြင့် sqlite database error ကင်းဝေးစေသည်
client = TelegramClient(StringSession(), api_id, api_hash)

async def get_video_stream(message_id, channel_id):
    try:
        # Client ကို connect လုပ်ခြင်း
        if not client.is_connected():
            await client.connect()
        
        # Bot အဖြစ် login ဝင်ခြင်း
        if not await client.is_user_authorized():
            await client.start(bot_token=bot_token)
        
        entity = await client.get_entity(int(channel_id))
        message = await client.get_messages(entity, ids=int(message_id))
        
        if message and message.video:
            # chunk_size ကို နည်းနည်းလျှော့ကြည့်ပါ (ပိုမြန်စေရန်)
            async for chunk in client.iter_download(message.video, chunk_size=512*1024):
                yield chunk
    except Exception as e:
        print(f"Streaming Error: {e}")