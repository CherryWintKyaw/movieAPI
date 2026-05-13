import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import messaging
from ..models import FCMDevice
from ..serializers import FCMDeviceSerializer

# Error log တွေကို စစ်လို့ရအောင်
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_fcm_token(request):
    """
    Mobile App ကနေ ပို့လိုက်တဲ့ FCM Token ကို လက်ခံသိမ်းဆည်းပေးမယ့် API ဖြစ်ပါတယ်။
    """
    serializer = FCMDeviceSerializer(data=request.data)
    
    if serializer.is_valid():
        fcm_token = serializer.validated_data.get('fcm_token')
        device_type = serializer.validated_data.get('device_type')
        
        # လက်ရှိ login ဝင်ထားတဲ့ user ရှိရင် ယူမယ်၊ မရှိရင် None (Guest)
        user = request.user if request.user.is_authenticated else None

        # Token ရှိပြီးသားဆိုရင် User နဲ့ Device Type ကိုပဲ update လုပ်မယ်
        # မရှိသေးရင် record အသစ်ဆောက်မယ်
        device, created = FCMDevice.objects.update_or_create(
            fcm_token=fcm_token,
            defaults={
                'user': user,
                'device_type': device_type
            }
        )
        
        return Response({
            "message": "Successfully registered",
            "status": "created" if created else "updated"
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_push_notification(user_id, title, body, data=None):
    """
    သတ်မှတ်ထားတဲ့ User ဆီကို Push Noti ပို့ပေးမယ့် Helper Function ပါ။
    Database ထဲက အသုံးမဝင်တော့တဲ့ Token တွေကိုလည်း အလိုအလျောက် ရှင်းပေးပါတယ်။
    """
    # ၁။ User ရဲ့ Device Tokens အားလုံးကို ဆွဲထုတ်မယ်
    devices = FCMDevice.objects.filter(user_id=user_id)
    tokens = list(devices.values_list('fcm_token', flat=True))

    if not tokens:
        return "No registered tokens found for this user."

    # ၂။ Data values အားလုံးကို string ပြောင်းပေးဖို့ လိုပါတယ် (FCM requirement)
    fcm_data = {k: str(v) for k, v in data.items()} if data else None

    # ၃။ MulticastMessage အသုံးပြုပြီး အကုန်ပို့မယ်
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=fcm_data,
        tokens=tokens,
    )

    try:
        response = messaging.send_multicast(message)
        
        # ၄။ ပို့လို့မရတော့တဲ့ (ဥပမာ- App ဖျက်လိုက်လို့ သက်တမ်းကုန်သွားတဲ့) Token များကို ရှင်းထုတ်ခြင်း
        if response.failure_count > 0:
            invalid_tokens = []
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    # Token invalid ဖြစ်နေတဲ့ index ကို ရှာပြီး tokens list ထဲက ယူမယ်
                    invalid_tokens.append(tokens[idx])
            
            # Database ကနေ အဲဒီ Token အဟောင်းတွေကို ဖျက်မယ်
            if invalid_tokens:
                FCMDevice.objects.filter(fcm_token__in=invalid_tokens).delete()
                logger.info(f"Cleaned up {len(invalid_tokens)} invalid tokens.")

        return f"Successfully sent {response.success_count} messages. Failures: {response.failure_count}"

    except Exception as e:
        logger.error(f"FCM Multicast Error: {e}")
        return f"Error sending notification: {str(e)}"

@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_broadcast_noti(request):
    """
    React-Admin panel ကနေ Noti လှမ်းပို့ချင်ရင် သုံးဖို့ API View ပါ။
    """
    title = request.data.get('title')
    body = request.data.get('body')
    user_id = request.data.get('user_id')

    if not all([title, body, user_id]):
        return Response({"error": "Title, Body, and User ID are required"}, status=400)

    result = send_push_notification(user_id, title, body)
    return Response({"result": result})