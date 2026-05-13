from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Series
from ..serializers import SeriesSerializer

from rest_framework.pagination import PageNumberPagination

@api_view(['GET'])
def series_list(request):
    series_queryset = Series.objects.all().order_by('-created_at')
    
    # Pagination object ကို ဆောက်မယ်
    paginator = PageNumberPagination()
    paginator.page_size = 3 # တစ်မျက်နှာမှာ ပြချင်တဲ့ item အရေအတွက်
    
    # Queryset ကို paginate လုပ်မယ်
    paginated_series = paginator.paginate_queryset(series_queryset, request)
    
    # Serializer မှာ paginated data ကို ထည့်ပေးမယ်
    serializer = SeriesSerializer(paginated_series, many=True)
    
    # Paginator ရဲ့ response format အတိုင်း ပြန်ပေးမယ် (count, next, previous ပါလာလိမ့်မယ်)
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


