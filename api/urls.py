from django.urls import path
from .views import banner_view

urlpatterns = [
    path('banner_list/', banner_view.banner_list, name='banner_list'),
    path('banner_create/', banner_view.banner_create, name='banner_create'),
    path('banner_detail/<uuid:pk>/', banner_view.banner_detail, name='banner_detail'),
    path('banner_update/<uuid:pk>/', banner_view.banner_update, name='banner_update'),
    path('banner_delete/<uuid:pk>/', banner_view.banner_delete, name='banner_delete'),
    path('banner_delete_all/', banner_view.banner_all_delete, name='banner_delete_all'),
]