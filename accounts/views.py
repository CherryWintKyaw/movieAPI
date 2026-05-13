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
from .serializers import GroupSerializer
from django.db.models import Q, CharField
from django.db.models.functions import Cast

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
    """
    # Request ကလာတဲ့ data ကို ယူခြင်း
    identifier = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')

    # Data မပါလာပါက Error ပြန်ခြင်း
    if not identifier or not password:
        return Response({
            "error": "Please provide username/email and password",
            "message": "Username သို့မဟုတ် Password လိုအပ်နေပါသည်"
        }, status=status.HTTP_400_BAD_REQUEST)

    # User ကို authenticate လုပ်ခြင်း
    user = authenticate(username=identifier, password=password)

    if user is not None:
        if not user.is_active:
            return Response({
                "error": "This account is disabled",
                "message": "ဤအကောင့်မှာ အသုံးပြုခွင့် ပိတ်ပင်ခံထားရပါသည်"
            }, status=status.HTTP_403_FORBIDDEN)
            
        # Token များ ထုတ်ပေးခြင်း
        tokens = get_tokens_for_user(user)
        
        return Response({
            "message": "Login successful",  # ✅ အောင်မြင်ကြောင်း message ထည့်လိုက်သည်
            "tokens": tokens,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_premium": user.is_premium,
                "premium_expiry": user.premium_expiry
            }
        }, status=status.HTTP_200_OK)
    else:
        # User ရှာမတွေ့ပါက သို့မဟုတ် Password မှားပါက
        return Response({
            "error": "Invalid username/email or password",
            "message": "Username သို့မဟုတ် Password မှားယွင်းနေပါသည်"
        }, status=status.HTTP_401_UNAUTHORIZED)
    
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
@permission_classes([IsAdminUser])
def get_all_users(request):
    """
    User အားလုံးကို ID, Email, Username, Role နှင့် Premium Status 
    တို့ဖြင့် Search လုပ်နိုင်ပြီး Pagination ဖြင့် ပြသခြင်း
    """
    # 1. Queryset (Groups နှင့် Permissions ပါ တစ်ခါတည်း ဆွဲယူထားမည်)
    users = User.objects.all().prefetch_related('groups', 'user_permissions').order_by('-date_joined')
    
    # 2. Search Logic
    search_query = request.query_params.get('search', None)
    if search_query:
        # Boolean နှင့် Choices များကို စာသားပြောင်းပြီး ရှာနိုင်အောင် Annotation လုပ်မည်
        users = users.annotate(
            is_premium_str=Cast('is_premium', CharField()),
            id_str=Cast('id', CharField())
        ).filter(
            Q(id_str__icontains=search_query) |       # UUID ID
            Q(email__icontains=search_query) |        # User Email
            Q(username__icontains=search_query) |     # Username
            Q(role__icontains=search_query) |         # Role (customer/owner)
            Q(is_premium_str__icontains=search_query) # Premium (true/false)
        ).distinct()

    # 3. Pagination သတ်မှတ်မယ်
    paginator = PageNumberPagination()
    paginator.page_size = 10
    
    # 4. Result ထုတ်မယ်
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
    user = get_object_or_404(User, pk=pk)

    # Security: Admin မဟုတ်ရင် မိမိအကောင့်ကလွဲပြီး သူများအကောင့် ပြင်ခွင့်မရှိစေရ
    if not request.user.is_staff and request.user.id != user.id:
        return Response(
            {"error": "You do not have permission to update this user's data."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # Security: Group သို့မဟုတ် Permission ပြောင်းလဲရန် ကြိုးစားပါက Admin ဖြစ်မှသာ ခွင့်ပြုမည်
    if ('groups' in request.data or 'user_permissions' in request.data) and not request.user.is_staff:
        return Response(
            {"error": "Only admins can modify groups or permissions."},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = UserDetailSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "User updated successfully",
            "user": serializer.data
        }, status=status.HTTP_200_OK)

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
    """
    Django System ရှိ Permissions အားလုံးကို Name သို့မဟုတ် Codename ဖြင့် 
    Search လုပ်နိုင်ပြီး Pagination ဖြင့် ပြသခြင်း
    """
    # 1. Permission အားလုံးကို ယူမယ်
    perms = Permission.objects.all().order_by('content_type__app_label', 'codename')

    # 2. Search Logic (Name သို့မဟုတ် Codename ကို ရှာမယ်)
    search_query = request.query_params.get('search', None)
    if search_query:
        perms = perms.filter(
            Q(name__icontains=search_query) |       # ဥပမာ - "Can add movie"
            Q(codename__icontains=search_query)     # ဥပမာ - "add_movie"
        ).distinct()

    # 3. Pagination (Permissions က များနိုင်လို့ Pagination ထည့်သင့်ပါတယ်)
    paginator = PageNumberPagination()
    paginator.page_size = 20 # တစ်မျက်နှာ ၂၀ ခုစီပြမယ်
    
    result_page = paginator.paginate_queryset(perms, request)
    
    # Values ကိုသုံးထားရင် Serializer မလိုဘဲ တိုက်ရိုက် Response ပေးလို့ရပါတယ်
    # ဒါပေမဲ့ Pagination သုံးရင်တော့ serializer ကဲ့သို့ data structure ပြန်ပေးဖို့လိုပါတယ်
    data = [{
        'id': p.id,
        'name': p.name,
        'codename': p.codename,
        'content_type': str(p.content_type)
    } for p in result_page]

    return paginator.get_paginated_response(data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_groups(request):
    """
    System ထဲရှိ Groups (Roles) များကို Name သို့မဟုတ် ID ဖြင့် 
    Search လုပ်နိုင်ပြီး Pagination ဖြင့် ပြသခြင်း
    """
    # 1. Group အားလုံးကို အမည်အလိုက် စီပြီးယူမယ်
    groups_queryset = Group.objects.all().order_by('name')

    # 2. Search Logic (Group Name သို့မဟုတ် ID ကို ရှာမယ်)
    search_query = request.query_params.get('search', None)
    if search_query:
        groups_queryset = groups_queryset.filter(
            Q(name__icontains=search_query) |
            Q(id__icontains=search_query)
        ).distinct()

    # 3. Pagination သတ်မှတ်မယ်
    paginator = PageNumberPagination()
    paginator.page_size = 10
    
    result_page = paginator.paginate_queryset(groups_queryset, request)
    
    # Data Format ကို စနစ်တကျ ပြန်ထုတ်မယ်
    data = [{
        'id': g.id,
        'name': g.name,
        'permissions_count': g.permissions.count() # Group ထဲမှာ permission ဘယ်နှစ်ခုရှိလဲပါ ထည့်ပေးထားတယ်
    } for g in result_page]

    return paginator.get_paginated_response(data)

# --- 1. Create Group ---
@api_view(['POST'])
@permission_classes([IsAdminUser])
def group_create(request):
    """Group အသစ်ဆောက်ရန်"""
    serializer = GroupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 2. List & Detail Group ---
@api_view(['GET'])
@permission_classes([IsAdminUser])
def group_detail(request, pk):
    """Group တစ်ခုချင်းစီ၏ အသေးစိတ်ကို ကြည့်ရန်"""
    group = get_object_or_404(Group, pk=pk)
    serializer = GroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_200_OK)

# --- 3. Update Group ---
@api_view(['PATCH', 'PUT'])
@permission_classes([IsAdminUser])
def group_update(request, pk):
    """Group အမည် သို့မဟုတ် Permission များကို ပြင်ရန်"""
    group = get_object_or_404(Group, pk=pk)
    serializer = GroupSerializer(group, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 4. Delete Single Group ---
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def group_delete(request, pk):
    """Group တစ်ခုတည်းကို ဖျက်ရန်"""
    group = get_object_or_404(Group, pk=pk)
    group.delete()
    return Response({"message": "Group deleted successfully"}, status=status.HTTP_200_OK)

# --- 5. Delete All Groups ---
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def group_delete_all(request):
    """Group အားလုံးကို တစ်ခါတည်းဖျက်ရန်"""
    groups = Group.objects.all()
    count = groups.count()
    groups.delete()
    return Response({"message": f"Successfully deleted {count} groups."}, status=status.HTTP_200_OK)

