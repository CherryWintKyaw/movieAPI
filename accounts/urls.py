from django.urls import path
from .views import register_user, login_user,get_all_users, get_user_detail, update_user, delete_user, delete_all_users, get_all_permissions
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
]