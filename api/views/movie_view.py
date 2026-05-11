from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse
from asgiref.sync import sync_to_async
from rest_framework.pagination import PageNumberPagination

from ..models import Movie
from ..serializers import MovieSerializer
from ..telegram_utils import get_video_stream
from django.urls import reverse

# --- 1. Movie List (ရုပ်ရှင်အားလုံးကို ပြရန်) ---
@api_view(['GET'])
def movie_list(request):
    # 1. Data အားလုံးကို ဆွဲထုတ်မယ် (Pagination လုပ်ရင် order_by ထည့်ပေးဖို့ အကြံပြုလိုပါတယ်)
    movies = Movie.objects.all().order_by('id')
    
    # 2. Paginator object ကို တည်ဆောက်ပြီး page size သတ်မှတ်မယ်
    paginator = PageNumberPagination()
    paginator.page_size = 10 # တစ်မျက်နှာမှာ ပြလိုတဲ့ အရေအတွက်
    
    # 3. Queryset ကို paginate လုပ်မယ်
    result_page = paginator.paginate_queryset(movies, request)
    
    # 4. ရလာတဲ့ result_page (စာမျက်နှာတစ်ခုစာ data) ကိုပဲ serialize လုပ်မယ်
    serializer = MovieSerializer(result_page, many=True)
    
    # 5. Paginated response (next, previous links ပါဝင်သော response) ကို return ပြန်မယ်
    return paginator.get_paginated_response(serializer.data)

# --- 2. Movie Create (ရုပ်ရှင်အသစ် သိမ်းရန်) ---
@api_view(['POST'])
def movie_create(request):
    serializer = MovieSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 3. Movie Detail (ရုပ်ရှင်တစ်ခုချင်းစီကို UUID ဖြင့် ကြည့်ရန်) ---
@api_view(['GET'])
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)

# --- 4. Movie Update (ရုပ်ရှင်အချက်အလက် ပြင်ရန်) ---
@api_view(['PUT', 'PATCH'])
def movie_update(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    # partial=True က patch အတွက် (အကုန်မပို့ဘဲ တစ်ခုချင်းပြင်ချင်ရင် သုံးနိုင်သည်)
    serializer = MovieSerializer(movie, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 5. Movie Delete (ရုပ်ရှင်တစ်ခုကို ဖျက်ရန်) ---
@api_view(['DELETE'])
def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    movie_title = movie.title  # (Optional) နာမည်လေးပါ ပြချင်ရင် သိမ်းထားလို့ရပါတယ်
    movie.delete()
    
    return Response(
        {"message": f"Movie '{movie_title}' deleted successfully!"}, 
        status=status.HTTP_200_OK
    )

# --- Movie အားလုံးကို ဖျက်ရန် ---
@api_view(['DELETE'])
def movie_all_delete(request):
    # ဖျက်လိုက်တဲ့ အရေအတွက်ကို သိချင်ရင် count() အရင်လုပ်ပါ
    count = Movie.objects.all().count()
    Movie.objects.all().delete()
    
    return Response(
        {"message": f"Total {count} movies have been deleted successfully!"}, 
        status=status.HTTP_200_OK
    )

# --- 7. Movie Play (Video Streaming လုပ်ရန်) ---
# နာမည်ကို movie_stream လို ပြောင်းလိုက်ပါ
def movie_stream(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    stream_gen = get_video_stream(movie.telegram_message_id, movie.telegram_channel_id)
    response = StreamingHttpResponse(stream_gen, content_type=movie.mime_type)
    response['Accept-Ranges'] = 'bytes'
    return response

@api_view(['GET'])
def movie_play_api(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    
    # ဗီဒီယို stream လုပ်မယ့် URL ကို တည်ဆောက်မယ်
    # အပေါ်က movie_stream function ဆီကို သွားမယ့် URL ပါ
    video_url = request.build_absolute_uri(reverse('movie_stream', args=[pk]))

    return Response({
        "status": "success",
        "video_link": video_url, # ဒီ link ကို App က ဖတ်ပြီး Player မှာ ဖွင့်ပါလိမ့်မယ်
        "title": movie.title,
        "mime_type": movie.mime_type
    })