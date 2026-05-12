from django.urls import path
from .views import banner_view, country_view, genre_view, director_view, cast_view, premiere_view, rating_view, movie_view, series_view

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

    path('genre_list/', genre_view.genre_list, name='genre_list'),
    path('genre_create/', genre_view.genre_create, name='genre_create'),
    path('genre_detail/<uuid:pk>/', genre_view.genre_detail, name='genre_detail'),
    path('genre_update/<uuid:pk>/', genre_view.genre_update, name='genre_update'),
    path('genre_delete/<uuid:pk>/', genre_view.genre_delete, name='genre_delete'),
    path('genre_delete_all/', genre_view.genre_all_delete, name='genre_delete_all'),

    path('director_list/', director_view.director_list, name='director_list'),
    path('director_create/', director_view.director_create, name='director_create'),
    path('director_detail/<uuid:pk>/', director_view.director_detail, name='director_detail'),
    path('director_update/<uuid:pk>/', director_view.director_update, name='director_update'),
    path('director_delete/<uuid:pk>/', director_view.director_delete, name='director_delete'),
    path('director_delete_all/', director_view.director_all_delete, name='director_delete_all'),

    path('cast_list/', cast_view.cast_list, name='cast_list'),
    path('cast_create/', cast_view.cast_create, name='cast_create'),
    path('cast_detail/<uuid:pk>/', cast_view.cast_detail, name='cast_detail'),
    path('cast_update/<uuid:pk>/', cast_view.cast_update, name='cast_update'),
    path('cast_delete/<uuid:pk>/', cast_view.cast_delete, name='cast_delete'),
    path('cast_delete_all/', cast_view.cast_all_delete, name='cast_delete_all'),

    path('premiere_list/', premiere_view.premiere_list, name='premiere_list'),
    path('premiere_create/', premiere_view.premiere_create, name='premiere_create'),
    path('premiere_detail/<uuid:pk>/', premiere_view.premiere_detail, name='premiere_detail'),
    path('premiere_update/<uuid:pk>/', premiere_view.premiere_update, name='premiere_update'),
    path('premiere_delete/<uuid:pk>/', premiere_view.premiere_delete, name='premiere_delete'),
    path('premiere_delete_all/', premiere_view.premiere_all_delete, name='premiere_delete_all'),

    path('rating_list/', rating_view.rating_list, name='rating_list'),
    path('rating_create/', rating_view.rating_create, name='rating_create'),
    path('rating_detail/<uuid:pk>/', rating_view.rating_detail, name='rating_detail'),
    path('rating_update/<uuid:pk>/', rating_view.rating_update, name='rating_update'),
    path('rating_delete/<uuid:pk>/', rating_view.rating_delete, name='rating_delete'),
    path('rating_delete_all/', rating_view.rating_all_delete, name='rating_delete_all'),

# ၁။ ရုပ်ရှင်အားလုံးစာရင်း (Home Screen အတွက်)
    # GET /api/movies/
    path('movies_list/', movie_view.movie_list, name='movie-list'),

    # ၂။ Trending ဖြစ်နေသော ရုပ်ရှင်များ
    # GET /api/movies/trending/
    path('movies/trending/', movie_view.trending_movies, name='trending-movies'),

    # ၃။ ရုပ်ရှင်ရှာဖွေရန် API
    # GET /api/movies/search/?q=...
    path('movies/search/', movie_view.search_movies, name='search-movies'),

    # ၄။ ရုပ်ရှင်အသေးစိတ်ကြည့်ရန် (Slug ကို သုံးထားသည်)
    # GET /api/movies/movie-slug-name/
    # urls.py
    path('movies_detail/<uuid:movie_uuid>/', movie_view.movie_detail, name='movie-detail'),
# ၅။ Video Play URL သီးသန့်ယူရန် (Optional)
    # GET /api/movies/video/1/
    path('movies/video/<int:video_id>/', movie_view.get_play_url, name='get-play-url'),

    path('movies_create/', movie_view.movie_create_view, name='movie_create'),

    path('movies_update/<uuid:pk>/', movie_view.movie_update, name='movie_update'),
    path('movies_delete/<uuid:pk>/', movie_view.movie_delete, name='movie_delete'),
    path('movies_delete_all/', movie_view.movie_delete_all, name='movie_delete_all'),

    path('series_list/', series_view.series_list, name='series_list'),
    path('series_create/', series_view.series_create, name='series_create'),
    path('series_detail/<uuid:pk>/', series_view.series_detail, name='series_detail'),
    path('series_update/<uuid:pk>/', series_view.series_update, name='series_update'),
    path('series_delete/<uuid:pk>/', series_view.series_delete, name='series_delete'),
    path('series_delete_all/', series_view.series_delete_all, name='series_delete_all'),


]

