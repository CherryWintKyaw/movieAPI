from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users_list/', get_all_users, name='user_list'),
    path('users_detail/<uuid:pk>/', get_user_detail, name='user_detail'),
    path('users_update/<uuid:pk>/', update_user, name='user_update'),
    path('users_delete/<uuid:pk>/', delete_user, name='user_delete'),
    path('users_delete_all/', delete_all_users, name='delete_all_users'),
    path('permissions/', get_all_permissions, name='all_permissions'),

    path('groups_list/', get_all_groups, name='all_groups'),            # Group အကုန်ကြည့်ရန်
    path('groups_create/', group_create, name='group_create'),       # Group အသစ်ဆောက်ရန်
    path('groups_detail/<int:pk>/', group_detail, name='group_detail'), # Detail ကြည့်ရန်
    path('groups_update/<int:pk>/', group_update, name='group_update'), # Update လုပ်ရန်
    path('groups_delete/<int:pk>/', group_delete, name='group_delete'), # တစ်ခုတည်းဖျက်ရန်
    path('groups_delete_all/', group_delete_all, name='group_delete_all'), # အကုန်ဖျက်ရန်
]