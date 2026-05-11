from telethon import functions, types

async def get_video_stream(message_id, channel_id):
    try:
        # channel_id က -100 ပါတာ/မပါတာကို handle လုပ်မယ်
        if str(channel_id).startswith('-100'):
            entity_id = int(channel_id)
        else:
            entity_id = int(f"-100{channel_id}")

        # ၁။ Entity ကို အရင်ယူပါ (ဒါမှ Channel လား၊ Group လား ကွဲမှာပါ)
        entity = await client.get_entity(entity_id)
        
        # ၂။ Message ကို ဆွဲထုတ်ပါ
        message = await client.get_messages(entity, ids=message_id)
        
        if message and message.video:
            # ၃။ Generator နဲ့ data chunk တွေကို ပို့ပေးပါ
            async for chunk in client.iter_download(message.video):
                yield chunk
    except Exception as e:
        print(f"❌ Telegram Utility Error: {str(e)}")
        yield b"" # Error ဖြစ်ရင် empty byte ပြန်ပေးမယ်