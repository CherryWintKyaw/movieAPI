from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import FCMDevice
from ..serializers import FCMDeviceSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register_fcm_token(request):
    """
    Mobile ကနေပို့လိုက်တဲ့ FCM Token ကို လက်ခံသိမ်းဆည်းပေးမယ့် function ပါ။
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