from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Movie, MovieVideo
from ..serializers import MovieVideoSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

# ၁။ Movie Video List (ဗီဒီယိုအားလုံးကို ကြည့်ရန်)
@api_view(['GET'])
def movie_video_list(request):
    """
    Movie ဗီဒီယိုများကို Movie Title, Quality, File Size, Duration 
    သို့မဟုတ် File Code တို့ဖြင့် Search လုပ်နိုင်ပြီး Pagination ဖြင့် ပြသခြင်း
    """
    # 1. ဗီဒီယိုအားလုံးကို Movie Name အလိုက် အစဉ်လိုက်ယူမယ်
    videos = MovieVideo.objects.select_related('movie').all().order_by('movie__title', 'quality')
    
    # 2. Search Logic (Field အားလုံးနီးပါး ပါဝင်သည်)
    search_query = request.query_params.get('search', None)
    if search_query:
        videos = videos.filter(
            Q(movie__title__icontains=search_query) |    # Movie Title နဲ့ ရှာမယ်
            Q(quality__icontains=search_query) |         # Quality (720p, 1080p, etc.)
            Q(dood_file_code__icontains=search_query) |  # DoodStream File Code
            Q(file_size__icontains=search_query) |       # 1.2 GB စသည်ဖြင့်
            Q(duration__icontains=search_query)          # 1h 52m စသည်ဖြင့်
        ).distinct()

    # 3. Pagination သတ်မှတ်မယ်
    paginator = PageNumberPagination()
    paginator.page_size = 10
    
    # 4. Result ကို Serialize လုပ်မယ်
    result_page = paginator.paginate_queryset(videos, request)
    serializer = MovieVideoSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# ၂။ Movie Video Create (ဗီဒီယိုအသစ်ထည့်ရန်)
@api_view(['POST'])
def movie_video_create(request):
    serializer = MovieVideoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Video link added successfully!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ၃။ Movie Video Detail (တစ်ခုတည်းကို အသေးစိတ်ကြည့်ရန်)
@api_view(['GET'])
def movie_video_detail(request, pk):
    video = get_object_or_404(MovieVideo, id=pk)
    serializer = MovieVideoSerializer(video)
    return Response(serializer.data)

# ၄။ Movie Video Update (အရည်အသွေး သို့မဟုတ် link ကို ပြင်ရန်)
@api_view(['PUT', 'PATCH'])
def movie_video_update(request, pk):
    video = get_object_or_404(MovieVideo, id=pk)
    serializer = MovieVideoSerializer(video, data=request.data, partial=True)
    
    if serializer.is_valid():
        # စစ်ဆေးချက်- request.data ထဲမှာ ပြင်စရာ data ပါမပါ ကြည့်မယ်
        if not request.data:
            return Response({
                "status": "no_change",
                "message": "No data provided to update.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        serializer.save()
        return Response({
            "status": "success",
            "message": "Video updated successfully!",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ၅။ Movie Video Delete (ဗီဒီယိုတစ်ခုကို ဖျက်ရန်)
@api_view(['DELETE'])
def movie_video_delete(request, pk):
    video = get_object_or_404(MovieVideo, id=pk)
    movie_title = video.movie.title
    quality = video.quality
    video.delete()
    return Response({
        "status": "success",
        "message": f"Video ({quality}) for '{movie_title}' deleted successfully!"
    }, status=status.HTTP_200_OK)

# ၆။ Movie Video Delete All (ဗီဒီယိုအားလုံးကို တစ်ခါတည်းဖျက်ရန်)
@api_view(['DELETE'])
def movie_video_delete_all(request):
    count = MovieVideo.objects.count()
    if count == 0:
        return Response({"message": "No videos found to delete."}, status=status.HTTP_404_NOT_FOUND)
    
    MovieVideo.objects.all().delete()
    return Response({
        "status": "success",
        "message": f"All {count} movie videos deleted successfully!"
    }, status=status.HTTP_200_OK)