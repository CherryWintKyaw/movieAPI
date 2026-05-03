# accounts/authentication_backend.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Login ဝင်တဲ့အခါ ရိုက်ထည့်လိုက်တဲ့ string ဟာ email ဖြစ်ဖြစ် username ဖြစ်ဖြစ် ရှာမယ်
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None