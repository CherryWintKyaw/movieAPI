from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from ..models import Episode
from ..serializers import EpisodeSerializer

# ၁။ Episode List (Pagination ပါဝင်သည်)
@api_view(['GET'])
def episode_list(request):
    # Series, Season, Episode အစဉ်လိုက် စီပေးထားပါတယ်
    episodes = Episode.objects.all().order_by('season__series', 'season', 'episode_number')
    
    paginator = PageNumberPagination()
    paginator.page_size = 3
    
    paginated_episodes = paginator.paginate_queryset(episodes, request)
    serializer = EpisodeSerializer(paginated_episodes, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# ၂။ Episode Create
# ဥပမာ Episode Create View
@api_view(['POST'])
def episode_create(request):
    # context ထည့်ပေးရန်
    serializer = EpisodeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Episode with video uploaded!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ၃။ Episode Detail
@api_view(['GET'])
def episode_detail(request, pk):
    episode = get_object_or_404(Episode, id=pk)
    serializer = EpisodeSerializer(episode)
    return Response(serializer.data)

# ၄။ Episode Update
@api_view(['PUT', 'PATCH'])
def episode_update(request, pk):
    episode = get_object_or_404(Episode, id=pk)
    # partial=True ကြောင့် video_file ကို မပြောင်းလဲဘဲ title ပဲ ပြင်တာမျိုး လုပ်နိုင်သည်
    serializer = EpisodeSerializer(episode, data=request.data, partial=True)
    
    if serializer.is_valid():
        if serializer.validated_data:
            serializer.save()
            return Response({
                "status": "success",
                "message": "Episode updated successfully!",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": "no_change",
            "message": "No changes detected.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ၅။ Episode Delete
@api_view(['DELETE'])
def episode_delete(request, pk):
    episode = get_object_or_404(Episode, id=pk)
    info = f"{episode.season.series.title} S{episode.season.season_number} E{episode.episode_number}"
    episode.delete()
    return Response({
        "status": "success",
        "message": f"'{info}' deleted successfully!"
    }, status=status.HTTP_200_OK)

# ၆။ Episode Delete All
@api_view(['DELETE'])
def episode_delete_all(request):
    count = Episode.objects.count()
    if count == 0:
        return Response({"message": "No episodes to delete."}, status=status.HTTP_404_NOT_FOUND)
    
    Episode.objects.all().delete()
    return Response({
        "status": "success",
        "message": f"All {count} episodes deleted successfully!"
    }, status=status.HTTP_200_OK)