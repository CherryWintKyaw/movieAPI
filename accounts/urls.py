from django.urls import path
from .views import register_user, login_user,get_all_users, get_user_detail
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users_list/', get_all_users, name='user_list'),
    path('users_detail/<uuid:pk>/', get_user_detail, name='user_detail'),
]