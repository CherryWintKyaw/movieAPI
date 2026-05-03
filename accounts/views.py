from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer

def get_tokens_for_user(user):
    """
    User object တစ်ခုအတွက် Access နှင့် Refresh Token ကို manual ထုတ်ပေးသော function
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    User အသစ် Register လုပ်ရန် (Email, Username, Password, Confirm Password)
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            "message": "User registered successfully",
            "tokens": tokens,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login ဝင်ရန် (Username သို့မဟုတ် Email + Password)
    ဒီ function က Username ရော Email ကိုပါ လက်ခံနိုင်ဖို့ settings.py မှာ 
    Custom Backend ချိတ်ထားဖို့ လိုပါတယ်။
    """
    # Postman ကနေ 'username' ဆိုတဲ့ key နဲ့ပဲ ဖြစ်စေ၊ 'email' ဆိုတဲ့ key နဲ့ပဲဖြစ်စေ ပို့နိုင်ပါတယ်
    # ဒါပေမဲ့ backend က username ဆိုတဲ့ parameter ကိုပဲ မျှော်လင့်ထားတာမို့လို့ပါ
    identifier = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')

    if not identifier or not password:
        return Response({"error": "Please provide username/email and password"}, status=status.HTTP_400_BAD_REQUEST)

    # settings.py ထဲက UsernameOrEmailBackend ကို အလိုအလျောက် သွားခေါ်ပါလိမ့်မယ်
    user = authenticate(username=identifier, password=password)

    if user is not None:
        if not user.is_active:
            return Response({"error": "This account is disabled"}, status=status.HTTP_403_FORBIDDEN)
            
        tokens = get_tokens_for_user(user)
        return Response({
            'tokens': tokens,
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_premium': user.is_premium,
                'premium_expiry': user.premium_expiry
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid username/email or password"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout လုပ်ရန် (Refresh token ကို blacklist ထဲထည့်ခြင်း)
    """
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"error": "Invalid token or already logged out"}, status=status.HTTP_400_BAD_REQUEST)