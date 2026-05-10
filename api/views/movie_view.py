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
async def movie_play(request, pk):
    # sync model ခေါ်ယူမှုကို async ပြောင်းပေးခြင်း
    movie = await sync_to_async(get_object_or_404)(Movie, pk=pk)
    
    if not movie.telegram_message_id or not movie.telegram_channel_id:
        from rest_framework.response import Response
        return Response({"error": "Video metadata missing"}, status=400)

    # View count ကို async ပုံစံဖြင့် တိုးပေးခြင်း
    movie.view_count += 1
    await sync_to_async(movie.save)()

    # StreamingHttpResponse ထဲကို async generator ကို တိုက်ရိုက်ထည့်ပေးခြင်း
    response = StreamingHttpResponse(
        get_video_stream(movie.telegram_message_id, movie.telegram_channel_id),
        content_type=movie.mime_type
    )
    
    # Range request header ထည့်ခြင်း
    response['Accept-Ranges'] = 'bytes'
    response['Cache-Control'] = 'no-cache'
    
    return response