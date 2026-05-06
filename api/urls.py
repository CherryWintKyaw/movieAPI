from django.urls import path
from .views import banner_view, country_view

urlpatterns = [
    path('banner_list/', banner_view.banner_list, name='banner_list'),
    path('banner_create/', banner_view.banner_create, name='banner_create'),
    path('banner_detail/<uuid:pk>/', banner_view.banner_detail, name='banner_detail'),
    path('banner_update/<uuid:pk>/', banner_view.banner_update, name='banner_update'),
    path('banner_delete/<uuid:pk>/', banner_view.banner_delete, name='banner_delete'),
    path('banner_delete_all/', banner_view.banner_all_delete, name='banner_delete_all'),

    path('country_list/', country_view.country_list, name='country_list'),
    path('country_create/', country_view.country_create, name='country_create'),
    path('country_detail/<uuid:pk>/', country_view.country_detail, name='country_detail'),
    path('country_update/<uuid:pk>/', country_view.country_update, name='country_update'),
    path('country_delete/<uuid:pk>/', country_view.country_delete, name='country_delete'),
    path('country_delete_all/', country_view.country_all_delete, name='country_delete_all'),
]

