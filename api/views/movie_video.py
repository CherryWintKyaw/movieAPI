from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Movie, MovieVideo
from ..serializers import MovieVideoSerializer

# ၁။ Movie Video List (ဗီဒီယိုအားလုံးကို ကြည့်ရန်)
@api_view(['GET'])
def movie_video_list(request):
    videos = MovieVideo.objects.all().order_by('movie', 'quality')
    serializer = MovieVideoSerializer(videos, many=True)
    return Response(serializer.data)

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