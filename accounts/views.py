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
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group

def get_tokens_for_user(user):
    """
    User တစ်ယောက်အတွက် Access/Refresh Tokens ထုတ်ပေးပြီး 
    User ရဲ့ Groups နှင့် Permissions အားလုံးကိုပါ Response မှာ ထည့်ပေးခြင်း
    """
    refresh = RefreshToken.for_user(user)
    
    # User ရဲ့ Direct Permissions ရော Group ကရတဲ့ Permissions ပါ အကုန်ယူခြင်း
    all_perms = list(user.get_all_permissions())
    groups = [group.name for group in user.groups.all()]
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user_details': {
            'groups': groups,
            'permissions': all_perms,
            'role': user.role,
            'is_premium': user.is_premium
        }
    }

# --- 1. Register User ---
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

# --- 2. Login User ---
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

# --- 3. Logout User ---
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
# --- 4. Get All Users (Admin Only) ---
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
    paginator.page_size = 3 # တစ်မျက်နှာမှာ user ၁၀ ယောက်စီ ပြမယ်
    
    result_page = paginator.paginate_queryset(users, request)
    serializer = UserListSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# --- 5. User Detail ---
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

# --- 6. Update User ---
@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, pk):
    """
    User အချက်အလက်များကို သီးသန့် Update လုပ်ရန် Function
    URL: /api/accounts/users_update/<uuid:pk>/
    """
    # ၁။ ပြင်ချင်တဲ့ User ကို ရှာမယ်
    user = get_object_or_404(User, pk=pk)

    # ၂။ Security Check: Admin မဟုတ်ရင် မိမိအကောင့်ကလွဲပြီး သူများအကောင့် ပြင်ခွင့်မရှိစေရ
    if not request.user.is_staff and request.user.id != user.id:
        return Response(
            {"error": "You do not have permission to update this user's data."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # ၃။ Serializer ထဲသို့ data များထည့်ပြီး စစ်ဆေးမယ်
    # partial=True ကြောင့် field အကုန်လုံးပို့စရာမလိုဘဲ ပြင်ချင်တာပဲ ပို့လို့ရပါတယ်
    serializer = UserDetailSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "User updated successfully",
            "user": serializer.data
        }, status=status.HTTP_200_OK)

    # ၄။ Validation error ရှိရင် (ဥပမာ username တူနေတာမျိုး) error ပြန်မယ်
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 7. Delete Single User ---

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, pk):
    """
    User အကောင့်အား ဖျက်သိမ်းရန် Function
    URL: /api/accounts/users_delete/<uuid:pk>/
    """
    # ၁။ ဖျက်ချင်တဲ့ User ကို ရှာမယ်
    user = get_object_or_404(User, pk=pk)

    # ၂။ Security Check: 
    # Admin မဟုတ်လျှင် မိမိအကောင့်မှလွဲ၍ အခြားသူ၏အကောင့်ကို ဖျက်ခွင့်မပြုပါ
    if not request.user.is_staff and request.user.id != user.id:
        return Response(
            {"error": "You do not have permission to delete this user."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # ၃။ Database ထဲမှ ဖျက်ထုတ်ခြင်း
    user.delete()

    # ၄။ အောင်မြင်ကြောင်း message ပြန်မယ် (204 No Content သို့မဟုတ် 200 OK)
    return Response(
        {"message": f"User '{user.username}' has been deleted successfully."}, 
        status=status.HTTP_200_OK
    )

# --- 8. Delete All Users (Admin Only) ---

@api_view(['DELETE'])
@permission_classes([IsAdminUser]) # Admin/Staff သာလျှင် ခေါ်ယူနိုင်သည်
def delete_all_users(request):
    """
    User အားလုံးကို တစ်ပြိုင်နက် ဖျက်သိမ်းရန် (Admin Only)
    မှတ်ချက် - လက်ရှိ Login ဝင်ထားသော Admin မိမိကိုယ်တိုင်ကိုတော့ မဖျက်မိအောင် ချန်လှပ်ထားပါမည်။
    """
    # လက်ရှိ Admin ကလွဲပြီး ကျန်တဲ့ User တွေကို စစ်ထုတ်မယ်
    users_to_delete = User.objects.exclude(id=request.user.id)
    
    count = users_to_delete.count()
    
    if count == 0:
        return Response({"message": "No users to delete."}, status=status.HTTP_200_OK)

    # အကုန်လုံးကို တစ်ခါတည်း ဖျက်မည်
    users_to_delete.delete()

    return Response({
        "message": f"Successfully deleted {count} users.",
        "note": "Active admin account was not deleted."
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_permissions(request):
    """Django System တစ်ခုလုံးရှိ Permissions စာရင်းကို ပြရန်"""
    perms = Permission.objects.all().values('id', 'name', 'codename')
    return Response(perms)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_groups(request):
    """System ထဲမှာရှိတဲ့ Groups စာရင်းကို ID နှင့် Name ပြရန်"""
    groups = Group.objects.all().values('id', 'name')
    return Response(groups)