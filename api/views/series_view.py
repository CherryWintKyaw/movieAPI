from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Series
from ..serializers import SeriesSerializer
from django.db.models import Q, CharField
from rest_framework.pagination import PageNumberPagination
from django.db.models.functions import Cast as DbCast

@api_view(['GET'])
def series_list(request):
    """
    Series အားလုံးကို Title, Description, Country, Rating, Year, Genre, Director, Cast
    စသည့် Field အားလုံးနီးပါးဖြင့် Search လုပ်နိုင်ပြီး Pagination ဖြင့် ပြသခြင်း
    """
    search_query = request.query_params.get('search', None)
    
    # ၁။ Performance ကောင်းအောင် Relationship တွေကို တစ်ခါတည်း ဆွဲယူထားမယ်
    series_queryset = Series.objects.select_related(
        'country', 'rating', 'release_year'
    ).prefetch_related(
        'genres', 'directors', 'casts'
    ).all().order_by('-created_at')

    if search_query:
        # ၂။ ကိန်းဂဏန်း Field တွေကို စာသားပြောင်းပြီး ရှာနိုင်အောင် Annotation လုပ်မယ်
        series_queryset = series_queryset.annotate(
            rating_str=DbCast('rating__rating', CharField()),
            year_str=DbCast('release_year__year', CharField())
        ).filter(
            Q(title__icontains=search_query) |             # Series Title
            Q(description__icontains=search_query) |       # Description
            Q(country__country__icontains=search_query) |  # Country Name
            Q(rating_str__icontains=search_query) |        # Rating Number (e.g. 8.5)
            Q(year_str__icontains=search_query) |          # Premiere Year (e.g. 2024)
            Q(genres__genre__icontains=search_query) |     # Genre Name
            Q(directors__director__icontains=search_query)|# Director Name
            Q(casts__cast__icontains=search_query)         # Cast Name
        ).distinct()

    # ၃။ Pagination သတ်မှတ်မယ်
    paginator = PageNumberPagination()
    paginator.page_size = 3
    
    # ၄။ Result ထုတ်မယ်
    paginated_series = paginator.paginate_queryset(series_queryset, request)
    serializer = SeriesSerializer(paginated_series, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['POST'])
def series_create(request):
    serializer = SeriesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Series created successfully!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def series_detail(request, pk):
    series = get_object_or_404(Series, id=pk)
    # SeriesDetailSerializer အစား SeriesSerializer ကို သုံးပါ
    serializer = SeriesSerializer(series, context={'request': request}) 
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
def series_update(request, pk):
    series_obj = get_object_or_404(Series, id=pk)
    serializer = SeriesSerializer(series_obj, data=request.data, partial=True)
    
    if serializer.is_valid():
        # အချက်အလက် အသစ်ပါမှ save မည်
        if serializer.validated_data:
            serializer.save()
            return Response({
                "status": "success",
                "message": "Series updated successfully!",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": "no_change",
            "message": "No changes detected.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def series_delete(request, pk):
    series_obj = get_object_or_404(Series, id=pk)
    title = series_obj.title
    series_obj.delete()
    return Response({
        "status": "success",
        "message": f"Series '{title}' deleted successfully!"
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def series_delete_all(request):
    series_count = Series.objects.count()
    if series_count == 0:
        return Response({"message": "Nothing to delete."}, status=status.HTTP_404_NOT_FOUND)
    
    Series.objects.all().delete()
    return Response({
        "status": "success",
        "message": f"All {series_count} series deleted successfully!"
    }, status=status.HTTP_200_OK)


