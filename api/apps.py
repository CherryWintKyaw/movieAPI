import os
import firebase_admin
from firebase_admin import credentials
from django.apps import AppConfig
from django.conf import settings

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # ၁။ JSON file ရှိမရှိ အရင်စစ်မယ်
        # မင်း settings.py မှာ FIREBASE_SDK_PATH လို့ ပေးခဲ့ရင် အဲဒါကို သုံးပါ
        # ဒါမှမဟုတ် အခုလို တိုက်ရိုက် ပေါင်းရေးလည်း ရပါတယ်
        cred_path = os.path.join(settings.BASE_DIR, 'firebase-adminsdk.json')

        # ၂။ Firebase ကို တစ်ကြိမ်ပဲ Initialize လုပ်ဖို့ စစ်ဆေးမယ်
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK: Connected Successfully!")
            except Exception as e:
                print(f"Firebase Initialization Error: {e}")