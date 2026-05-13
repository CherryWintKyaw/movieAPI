from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Rating
from ..serializers import RatingSerializer
from django.db.models import Q, CharField

# 1. Rating List with Pagination
@api_view(['GET'])
def rating_list(request):
    """
    Rating တန်ဖိုးများကို ID (UUID) သို့မဟုတ် Rating Number ဖြင့် 
    Search လုပ်နိုင်ပြီး Pagination ဖြင့် ပြသခြင်း
    """
    # 1. Rating အားလုံးကို အမြင့်ဆုံးကနေ စီပြီးယူမယ်
    ratings = Rating.objects.all().order_by('-rating')
    
    # 2. Search Logic
    search_query = request.query_params.get('search', None)
    if search_query:
        # Rating (Decimal) ကို စာသား (CharField) အဖြစ် ပြောင်းပြီးမှ ရှာမယ်
        ratings = ratings.annotate(
            rating_str=Cast('rating', CharField())
        ).filter(
            Q(id__icontains=search_query) |      # UUID ID ကို ရှာမယ်
            Q(rating_str__icontains=search_query) # Rating နံပါတ်ကို စာသားအဖြစ် ရှာမယ်
        ).distinct()

    # 3. Pagination သတ်မှတ်မယ်
    paginator = PageNumberPagination()
    paginator.page_size = 10
    
    # 4. Result ကို Serialize လုပ်ပြီး ပြန်ပေးမယ်
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