from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Rating
from ..serializers import RatingSerializer

# 1. Rating List with Pagination
@api_view(['GET'])
def rating_list(request):
    """
    Rating တန်ဖိုးအားလုံးကို Pagination ဖြင့် ပြသခြင်း (အမြင့်ဆုံးကနေ အနိမ့်ဆုံးစဉ်ထားသည်)
    """
    ratings = Rating.objects.all().order_by('-rating')
    
    paginator = PageNumberPagination()
    paginator.page_size = 10
    
    result_page = paginator.paginate_queryset(ratings, request)
    serializer = RatingSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# 2. Rating Create
@api_view(['POST'])
def rating_create(request):
    """
    Rating အသစ် ထည့်သွင်းခြင်း (ဥပမာ - {"rating": 9.5})
    """
    serializer = RatingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Rating Detail
@api_view(['GET'])
def rating_detail(request, pk):
    rating_entry = get_object_or_404(Rating, pk=pk)
    serializer = RatingSerializer(rating_entry)
    return Response(serializer.data)

# 4. Rating Full Update
@api_view(['PUT'])
def rating_update(request, pk):
    """
    Rating အချက်အလက်ကို Full Update လုပ်ခြင်း
    """
    rating_entry = get_object_or_404(Rating, pk=pk)
    serializer = RatingSerializer(rating_entry, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 5. Rating Delete
@api_view(['DELETE'])
def rating_delete(request, pk):
    rating_entry = get_object_or_404(Rating, pk=pk)
    rating_entry.delete()
    return Response({'message': 'Rating deleted successfully!'}, status=status.HTTP_200_OK)

# 6. Rating All Delete
@api_view(['DELETE'])
def rating_all_delete(request):
    count = Rating.objects.all().count()
    Rating.objects.all().delete()
    return Response(
        {'message': f'Total {count} ratings deleted successfully!'}, 
        status=status.HTTP_200_OK
    )