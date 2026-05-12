from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Movie, MovieVideo
from ..serializers import MovieSerializer
from rest_framework.pagination import PageNumberPagination

# ၁။ ရုပ်ရှင်အားလုံးစာရင်း (Home Screen အတွက်)

from django.db.models import Q, CharField
from django.db.models.functions import Cast # ဒါလေး ထပ်ထည့်ရမယ်

@api_view(['GET'])
def movie_list(request):
    search_query = request.query_params.get('search', None)
    
    # ၁။ movies ယူတဲ့အခါ Relationship တွေကိုပါ တစ်ခါတည်းဆွဲယူထားမယ် (Speed ပိုမြန်အောင်)
    movies = Movie.objects.prefetch_related('casts', 'genres', 'directors').select_related('country', 'release_year').all().order_by('-created_at')

    if search_query:
        # ၂။ release_year__year (Integer) ကို စာသားပြောင်းပြီး ရှာမယ်
        movies = movies.annotate(
            year_str=Cast('release_year__year', CharField())
        ).filter(
            Q(title__icontains=search_query) |            # Movie.title
            Q(description__icontains=search_query) |      # Movie.description
            Q(casts__cast__icontains=search_query) |      # Cast.cast
            Q(directors__director__icontains=search_query)|# Director.director
            Q(genres__genre__icontains=search_query) |    # Genre.genre
            Q(country__country__icontains=search_query) | # Country.country (မင်း model ထဲက နာမည်)
            Q(year_str__icontains=search_query)           # Premiere.year (Cast လုပ်ထားတာ)
        ).distinct()

    # ၃။ Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10 
    
    result_page = paginator.paginate_queryset(movies, request)
    serializer = MovieSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# ၂။ Trending ဖြစ်နေတဲ့ ရုပ်ရှင်များ (၁၀ ကားစာ)
@api_view(['GET'])
def trending_movies(request):
    movies = Movie.objects.filter(is_trending=True).order_by('-view_count')[:10]
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)

# ၃။ ရုပ်ရှင်အသေးစိတ် (Detail View)
@api_view(['GET'])
# views.py

def movie_detail(request, movie_uuid):
    # slug=slug အစား uuid=movie_uuid နဲ့ ရှာပါမယ်
    movie = get_object_or_404(Movie, id=movie_uuid) 
    
    # ... ကျန်တဲ့ logic များ
    
    # User တစ်ခါဝင်ကြည့်ရင် View Count ကို ၁ တိုးမယ်
    movie.view_count += 1
    movie.save(update_fields=['view_count'])
    
    serializer = MovieSerializer(movie)
    return Response(serializer.data)

# ၄။ ရုပ်ရှင်ရှာဖွေရန် (Search)
@api_view(['GET'])
def search_movies(request):
    # URL ကနေ ?q= ဆိုတဲ့ query ကို ယူမယ်
    query = request.query_params.get('q', '')
    if query:
        # Title ထဲမှာ ပါဝင်နေရင် ရှာပေးမယ်
        movies = Movie.objects.filter(title__icontains=query).order_by('-created_at')
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)
    # ရှာတာမတွေ့ရင် အလွတ်ပြန်ပေးမယ်
    return Response([])

# ၅။ Video Play URL သီးသန့်ယူရန် (Optional)
@api_view(['GET'])
def get_play_url(request, video_id):
    video = get_object_or_404(MovieVideo, id=video_id)
    # Model ထဲက property ကို လှမ်းသုံးထားတယ်
    return Response({
        "status": "success",
        "play_url": video.embed_url,
        "quality": video.quality,
        "file_size": video.file_size,
        "duration": video.duration
    })

@api_view(['POST'])
def movie_create_view(request):
    if request.method == 'POST':
        serializer = MovieSerializer(data=request.data)
        
        if serializer.is_valid():
            # Movie object ကို အရင် save လုပ်ပါမယ်
            movie = serializer.save()
            
            # Many-to-Many fields တွေကို handle လုပ်ခြင်း (ဥပမာ- ID list နဲ့ လာခဲ့ရင်)
            # request data ထဲက genres, directors, casts id တွေကို ယူပြီး ချိတ်ပေးခြင်း
            genre_ids = request.data.get('genres_ids', [])
            director_ids = request.data.get('directors_ids', [])
            cast_ids = request.data.get('casts_ids', [])
            
            if genre_ids:
                movie.genres.set(genre_ids)
            if director_ids:
                movie.directors.set(director_ids)
            if cast_ids:
                movie.casts.set(cast_ids)
            
            # အချက်အလက်အသစ်နဲ့အတူ ပြန်ပြပေးဖို့ serializer ကို ပြန်ခေါ်ပါ
            full_serializer = MovieSerializer(movie)
            return Response(full_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT', 'PATCH'])
def movie_update(request, pk):
    movie = get_object_or_404(Movie, id=pk)
    
    serializer = MovieSerializer(
        movie, 
        data=request.data, 
        partial=True 
    )

    if serializer.is_valid():
        # ✅ Data တကယ် ပြောင်းလဲမှု ရှိမရှိ စစ်မယ်
        if serializer.validated_data and serializer.instance:
            # တကယ် save လိုက်ပြီ
            serializer.save()
            
            return Response({
                "status": "success",
                "message": "Movie updated successfully!",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # ဘာမှ မပြင်ဘဲ ပို့လာရင် ပြမယ့် message
            return Response({
                "status": "no_change",
                "message": "No changes detected.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
    
    # Validation error (ဥပမာ- title ကျန်ခဲ့တာမျိုး) ရှိရင် ပြမယ်
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def movie_delete(request, pk):
    movie = get_object_or_404(Movie, id=pk)
    movie_title = movie.title  # ဖျက်ပြီးရင် သုံးဖို့ title ကို ခဏသိမ်းထားမယ်
    movie.delete()
    
    return Response({
        "status": "success",
        "message": f"Movie '{movie_title}' has been deleted successfully!"
    }, status=status.HTTP_200_OK) # 👈 204 အစား 200 ကို သုံးပါ

@api_view(['DELETE'])
def movie_delete_all(request):
    movies = Movie.objects.all()
    count = movies.count()
    
    if count == 0:
        return Response({
            "status": "info",
            "message": "There are no movies to delete."
        }, status=status.HTTP_404_NOT_FOUND)
        
    movies.delete()
    
    return Response({
        "status": "success",
        "message": f"All {count} movies have been deleted successfully!"
    }, status=status.HTTP_200_OK) # 👈 204 အစား 200 ကို သုံးပါ