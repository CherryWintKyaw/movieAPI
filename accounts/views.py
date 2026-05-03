from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, UserListSerializer, UserDetailSerializer
from .models import User
from django.shortcuts import get_object_or_404

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
    

# --- New: User List with Pagination ---

@api_view(['GET'])
@permission_classes([IsAdminUser]) # Admin တွေပဲ ကြည့်ခွင့်ပေးထားတာပါ
def get_all_users(request):
    """
    User အားလုံးကို Pagination ဖြင့် ပြသခြင်း
    URL: /api/accounts/users/?page=1
    """
    users = User.objects.all().order_by('-date_joined')
    
    # Pagination configuration
    paginator = PageNumberPagination()
    paginator.page_size = 2 # တစ်မျက်နှာမှာ user ၁၀ ယောက်စီ ပြမယ်
    
    result_page = paginator.paginate_queryset(users, request)
    serializer = UserListSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_detail(request, pk):
    """
    User တစ်ယောက်ချင်းစီ၏ Detail (အချက်အလက်) ကို ကြည့်ရှုရန်သာ
    URL: /api/accounts/users/<uuid:pk>/
    """
    
    # ၁။ URL ထဲကပါလာတဲ့ ID (pk) နဲ့ User ကို ရှာမယ်
    user = get_object_or_404(User, pk=pk)

    # ၂။ လုံခြုံရေး စစ်ဆေးချက်: 
    # Admin မဟုတ်ရင် မိမိ ID မဟုတ်တဲ့ တခြားသူရဲ့ data ကို ကြည့်ခွင့်မပေးဘူး
    if not request.user.is_staff and request.user.id != user.id:
        return Response(
            {"error": "You do not have permission to view this user's data."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # ၃။ Premium သက်တမ်း ကုန်/မကုန် Model ထဲက function နဲ့ စစ်မယ်
    user.check_premium_status()

    # ၄။ Serializer သုံးပြီး Data ကို JSON ပုံစံပြောင်းပြီး Return ပြန်မယ်
    serializer = UserDetailSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)