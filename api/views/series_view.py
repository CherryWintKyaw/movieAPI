from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination

from ..models import Series
from ..serializers import SeriesSerializer

# --- 1. Series List (Pagination ပါဝင်သည်) ---
@api_view(['GET'])
def series_list(request):
    series_queryset = Series.objects.all().order_by('-created_at')
    
    paginator = PageNumberPagination()
    paginator.page_size = 10
    
    result_page = paginator.paginate_queryset(series_queryset, request)
    serializer = SeriesSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# --- 2. Series Create ---
@api_view(['POST'])
def series_create(request):
    serializer = SeriesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 3. Series Detail (UUID ဖြင့် ကြည့်ရန်) ---
@api_view(['GET'])
def series_detail(request, pk):
    series = get_object_or_404(Series, pk=pk)
    serializer = SeriesSerializer(series)
    return Response(serializer.data)

# --- 4. Series Update ---
@api_view(['PUT', 'PATCH'])
def series_update(request, pk):
    series = get_object_or_404(Series, pk=pk)
    serializer = SeriesSerializer(series, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 5. Series Delete (တစ်ခုချင်းစီ) ---
@api_view(['DELETE'])
def series_delete(request, pk):
    series = get_object_or_404(Series, pk=pk)
    series_title = series.title
    series.delete()
    return Response(
        {"message": f"Series '{series_title}' deleted successfully!"}, 
        status=status.HTTP_200_OK
    )

# --- 6. Series All Delete (အားလုံးကို ဖျက်ရန်) ---
@api_view(['DELETE'])
def series_all_delete(request):
    count = Series.objects.all().count()
    Series.objects.all().delete()
    return Response(
        {"message": f"Total {count} series have been deleted successfully!"}, 
        status=status.HTTP_200_OK
    )