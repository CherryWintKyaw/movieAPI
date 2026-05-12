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
def movie_detail(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    
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