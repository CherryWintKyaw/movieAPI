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

# --- Async Generator ကို Sync Iterator အဖြစ် Warning ကင်းစွာ ပြောင်းပေးမည့် Wrapper ---
class AsyncToSyncIterator:
    def __init__(self, async_gen):
        self.async_gen = async_gen

    def __iter__(self):
        return self

    def __next__(self):
        try:
            # Lambda သို့မဟုတ် Async function အနေဖြင့် wrap လုပ်ခြင်းက asgiref UserWarning ကို ပျောက်စေပါသည်
            async def get_next():
                return await self.async_gen.__anext__()
            
            return async_to_sync(get_next)()
        except StopAsyncIteration:
            raise StopIteration
        except Exception as e:
            print(f"Streaming Error: {e}")
            raise StopIteration

# --- 1. Movie List (Pagination ပါဝင်သည်) ---
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
    title = movie.title
    movie.delete()
    return Response({"message": f"Movie '{title}' deleted!"}, status=status.HTTP_200_OK)

# --- 6. Movie All Delete ---
@api_view(['DELETE'])
def movie_all_delete(request):
    Movie.objects.all().delete()
    return Response({"message": "All movies deleted!"}, status=status.HTTP_200_OK)

# --- 7. Movie Stream (တကယ့် Video Data ကို Buffer လုပ်ပေးမည့် နေရာ) ---
def movie_stream(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    
    # ၁။ Telegram Async Generator ကို ခေါ်ယူသည်
    async_gen = get_video_stream(movie.telegram_message_id, movie.telegram_channel_id)
    
    # ၂။ Sync Wrapper ဖြင့် Iterator အဖြစ် ပြောင်းသည်
    sync_gen = AsyncToSyncIterator(async_gen)

    # ၃။ Streaming Response ကို Header များနှင့်အတူ ပြန်ပေးသည်
    response = StreamingHttpResponse(sync_gen, content_type=movie.mime_type)
    
    # Player များ အလုပ်လုပ်ရန် မရှိမဖြစ် လိုအပ်သော Header များ
    response['Accept-Ranges'] = 'bytes'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    
    if movie.file_size and int(movie.file_size) > 1:
        response['Content-Length'] = str(movie.file_size)
        
    return response

# --- 8. Movie Play API (App အတွက် ဗီဒီယို link ထုတ်ပေးရန်) ---
@api_view(['GET'])
def movie_play_api(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    
    # movie_stream URL ကို dynamic တည်ဆောက်သည်
    video_url = request.build_absolute_uri(reverse('movie_stream', args=[pk]))

    return Response({
        "status": "success",
        "data": {
            "id": movie.id,
            "title": movie.title,
            "video_link": video_url,
            "mime_type": movie.mime_type,
            "file_size": movie.file_size
        }
    })