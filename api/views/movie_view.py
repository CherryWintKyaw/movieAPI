from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Movie, MovieVideo
from ..serializers import MovieSerializer
from rest_framework.pagination import PageNumberPagination

# ၁။ ရုပ်ရှင်အားလုံးစာရင်း (Home Screen အတွက်)
@api_view(['GET'])
def movie_list(request):
    # ၁. Queryset ကို အရင်ယူမယ်
    movies = Movie.objects.all().order_by('-created_at')
    
    # ၂. Pagination Object ကို တည်ဆောက်မယ်
    paginator = PageNumberPagination()
    paginator.page_size = 2  # တစ်မျက်နှာမှာ ပြချင်တဲ့ item အရေအတွက်
    
    # ၃. ရလာတဲ့ movies ထဲက သက်ဆိုင်ရာ page အတွက် data ကို ခွဲထုတ်မယ်
    result_page = paginator.paginate_queryset(movies, request)
    
    # ၄. Serializer ထဲကို result_page (ခွဲထုတ်ပြီးသား data) ကို ထည့်မယ်
    serializer = MovieSerializer(result_page, many=True)
    
    # ၅. အဖြေပြန်ပေးတဲ့အခါ pagination metadata (next, previous, count) တွေပါအောင် ပြန်ပေးမယ်
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