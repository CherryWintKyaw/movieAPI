from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Movie, MovieVideo
from ..serializers import MovieSerializer, MovieListSerializer

# ၁။ ရုပ်ရှင်အားလုံးစာရင်း (Home Screen)
@api_view(['GET'])
def movie_list(request):
    movies = Movie.objects.all().order_by('-created_at')
    # MovieListSerializer အစား MovieSerializer ကို သုံးမယ်
    serializer = MovieSerializer(movies, many=True) 
    return Response(serializer.data)

@api_view(['GET'])
def trending_movies(request):
    movies = Movie.objects.filter(is_trending=True).order_by('-view_count')[:10]
    # ဒီမှာလည်း MovieSerializer ကိုပဲ သုံးမယ်
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)

# ၃။ ရုပ်ရှင်အသေးစိတ် (Detail View - Custom Player Metadata အတွက်)
@api_view(['GET'])
def movie_detail(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    
    # View Count ကို +1 တိုးမယ်
    movie.view_count += 1
    movie.save(update_fields=['view_count'])
    
    serializer = MovieSerializer(movie)
    return Response(serializer.data)

# ၄။ ရုပ်ရှင်ရှာဖွေရန် (Search)
@api_view(['GET'])
def search_movies(request):
    query = request.query_params.get('q', '')
    if query:
        movies = Movie.objects.filter(title__icontains=query).order_by('-created_at')
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)
    return Response([])

# ၅။ Video Play URL သီးသန့်ယူရန် (Optional - အကယ်၍ လိုအပ်ခဲ့ရင်)
@api_view(['GET'])
def get_play_url(request, video_id):
    video = get_object_or_404(MovieVideo, id=video_id)
    play_link = f"https://doodstream.com/e/{video.dood_file_code}"
    
    return Response({
        "status": "success",
        "play_url": play_link,
        "quality": video.quality
    })