from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse
from asgiref.sync import sync_to_async

from ..models import Movie
from ..serializers import MovieSerializer
from ..telegram_utils import get_video_stream

# --- 1. Movie List (ရုပ်ရှင်အားလုံးကို ပြရန်) ---
@api_view(['GET'])
def movie_list(request):
    movies = Movie.objects.all()
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)

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
    movie.delete()
    return Response({"message": "Movie deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

# --- 6. Movie All Delete (ရုပ်ရှင်အားလုံးကို ဖျက်ရန်) ---
@api_view(['DELETE'])
def movie_all_delete(request):
    Movie.objects.all().delete()
    return Response({"message": "All movies have been deleted!"}, status=status.HTTP_204_NO_CONTENT)

# --- 7. Movie Play (Video Streaming လုပ်ရန်) ---
@api_view(['GET'])
def movie_play(request, pk): # async ကို ဖြုတ်လိုက်ပါ
    movie = get_object_or_404(Movie, pk=pk)
    
    if not movie.telegram_message_id or not movie.telegram_channel_id:
        return Response({"error": "Video metadata missing"}, status=400)

    # View count တိုးခြင်း
    movie.view_count += 1
    movie.save()

    # async generator ကို sync context မှာ အလုပ်လုပ်အောင် wrap လုပ်ပေးရပါမယ်
    stream_gen = get_video_stream(movie.telegram_message_id, movie.telegram_channel_id)

    response = StreamingHttpResponse(
        stream_gen,
        content_type=movie.mime_type
    )
    response['Accept-Ranges'] = 'bytes'
    return response