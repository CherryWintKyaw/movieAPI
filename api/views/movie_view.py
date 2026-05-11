from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse
from asgiref.sync import async_to_sync
from rest_framework.pagination import PageNumberPagination
from django.urls import reverse

from ..models import Movie
from ..serializers import MovieSerializer
from ..telegram_utils import get_video_stream

# --- Async Generator ကို Sync Iterator အဖြစ် ပြောင်းပေးမည့် Wrapper ---
class AsyncToSyncIterator:
    def __init__(self, async_gen):
        self.async_gen = async_gen

    def __iter__(self):
        return self

    def __next__(self):
        try:
            # Async chunk ကို sync အနေနဲ့ ဆွဲထုတ်ပေးသည်
            return async_to_sync(self.async_gen.__anext__)()
        except StopAsyncIteration:
            raise StopIteration

# --- 1. Movie List ---
@api_view(['GET'])
def movie_list(request):
    movies = Movie.objects.all().order_by('-created_at')
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(movies, request)
    serializer = MovieSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# --- 2. Movie Create ---
@api_view(['POST'])
def movie_create(request):
    serializer = MovieSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 3. Movie Detail ---
@api_view(['GET'])
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)

# --- 4. Movie Update ---
@api_view(['PUT', 'PATCH'])
def movie_update(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    serializer = MovieSerializer(movie, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 5. Movie Delete ---
@api_view(['DELETE'])
def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    movie_title = movie.title
    movie.delete()
    return Response({"message": f"Movie '{movie_title}' deleted successfully!"}, status=status.HTTP_200_OK)

# --- 6. Movie All Delete ---
@api_view(['DELETE'])
def movie_all_delete(request):
    count = Movie.objects.all().count()
    Movie.objects.all().delete()
    return Response({"message": f"Total {count} movies deleted successfully!"}, status=status.HTTP_200_OK)

# --- 7. Movie Stream (တကယ့် Video Data ကို ပို့ပေးသည့်နေရာ) ---
def movie_stream(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    
    # ၁။ Telegram မှ Async Generator ကို ခေါ်ယူသည်
    async_gen = get_video_stream(movie.telegram_message_id, movie.telegram_channel_id)
    
    # ၂။ Async ကို Sync ပြောင်းပေးသည် (Warning ပျောက်စေရန်)
    sync_gen = AsyncToSyncIterator(async_gen)

    # ၃။ Response ထုတ်ပေးသည်
    response = StreamingHttpResponse(sync_gen, content_type=movie.mime_type)
    
    # ၄။ Player များအတွက် မရှိမဖြစ်လိုအပ်သော Header များ
    response['Accept-Ranges'] = 'bytes'
    
    # 🚩 File size က 1 ထက်ကြီးမှ Content-Length ထည့်ပေးမည် (Player အလုပ်လုပ်စေရန်)
    if movie.file_size and movie.file_size > 1:
        response['Content-Length'] = str(movie.file_size)
    else:
        # File Size မရှိလျှင် ခန့်မှန်းခြေ တစ်ခုခု ထည့်ပေးထားခြင်း (Optional)
        # response['Content-Length'] = "500000000" 
        pass
        
    return response

# --- 8. Movie Play API (App မှ video_link ယူရန်) ---
@api_view(['GET'])
def movie_play_api(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    video_url = request.build_absolute_uri(reverse('movie_stream', args=[pk]))

    return Response({
        "status": "success",
        "video_link": video_url,
        "title": movie.title,
        "mime_type": movie.mime_type
    })