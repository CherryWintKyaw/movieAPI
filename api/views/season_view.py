from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from ..models import Season
from ..serializers import SeasonSerializer

# ၁။ Season List (Pagination ပါဝင်သည်)
@api_view(['GET'])
def season_list(request):
    """
    Season များကို Series Title, Season Number သို့မဟုတ် Description ဖြင့် 
    Search လုပ်နိုင်ပြီး Pagination ဖြင့် ပြသခြင်း
    """
    search_query = request.query_params.get('search', None)
    
    # 1. Performance ကောင်းအောင် Series data ကို တစ်ခါတည်း ဆွဲယူထားမယ်
    seasons = Season.objects.select_related('series').all().order_by('series__title', 'season_number')

    if search_query:
        # 2. Season Number (Integer) ကို စာသားပြောင်းပြီး ရှာနိုင်အောင် လုပ်မယ်
        seasons = seasons.annotate(
            season_num_str=DbCast('season_number', CharField())
        ).filter(
            Q(id__icontains=search_query) |                # UUID ID
            Q(series__title__icontains=search_query) |     # Series Title (e.g. Money Heist)
            Q(season_num_str__icontains=search_query) |    # Season Number (e.g. 1, 2)
            Q(description__icontains=search_query)         # Season Description
        ).distinct()

    # 3. Pagination သတ်မှတ်မယ်
    paginator = PageNumberPagination()
    paginator.page_size = 2
    
    # 4. Result ထုတ်မယ်
    paginated_seasons = paginator.paginate_queryset(seasons, request)
    serializer = SeasonSerializer(paginated_seasons, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# ၂။ Season Create
@api_view(['POST'])
def season_create(request):
    serializer = SeasonSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Season created successfully!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ၃။ Season Detail
@api_view(['GET'])
def season_detail(request, pk):
    season = get_object_or_404(Season, id=pk)
    serializer = SeasonSerializer(season)
    return Response(serializer.data)

# ၄။ Season Update
@api_view(['PUT', 'PATCH'])
def season_update(request, pk):
    season = get_object_or_404(Season, id=pk)
    serializer = SeasonSerializer(season, data=request.data, partial=True)
    
    if serializer.is_valid():
        if serializer.validated_data:
            serializer.save()
            return Response({
                "status": "success",
                "message": "Season updated successfully!",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": "no_change",
            "message": "No changes detected.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ၅။ Season Delete
@api_view(['DELETE'])
def season_delete(request, pk):
    season = get_object_or_404(Season, id=pk)
    season_info = f"{season.series.title} - Season {season.season_number}"
    season.delete()
    return Response({
        "status": "success",
        "message": f"'{season_info}' deleted successfully!"
    }, status=status.HTTP_200_OK)

# ၆။ Season Delete All
@api_view(['DELETE'])
def season_delete_all(request):
    count = Season.objects.count()
    if count == 0:
        return Response({"message": "Nothing to delete."}, status=status.HTTP_404_NOT_FOUND)
    
    Season.objects.all().delete()
    return Response({
        "status": "success",
        "message": f"All {count} seasons deleted successfully!"
    }, status=status.HTTP_200_OK)