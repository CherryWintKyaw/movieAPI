from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Cast
from ..serializers import CastSerializer

# 1. Cast List with Pagination
@api_view(['GET'])
def cast_list(request):
    """
    သရုပ်ဆောင်အားလုံးကို Pagination ဖြင့် ပြသခြင်း
    """
    casts = Cast.objects.all().order_by('cast')
    
    paginator = PageNumberPagination()
    paginator.page_size = 10
    
    result_page = paginator.paginate_queryset(casts, request)
    serializer = CastSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# 2. Cast Create
@api_view(['POST'])
def cast_create(request):
    """
    သရုပ်ဆောင်အသစ် ထည့်သွင်းခြင်း (Image အတွက် form-data သုံးရန်)
    """
    serializer = CastSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Cast Detail
@api_view(['GET'])
def cast_detail(request, pk):
    cast_member = get_object_or_404(Cast, pk=pk)
    serializer = CastSerializer(cast_member)
    return Response(serializer.data)

# 4. Cast Full Update
@api_view(['PUT'])
def cast_update(request, pk):
    """
    သရုပ်ဆောင်အချက်အလက်ကို Full Update လုပ်ခြင်း
    """
    cast_member = get_object_or_404(Cast, pk=pk)
    serializer = CastSerializer(cast_member, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 5. Cast Delete
@api_view(['DELETE'])
def cast_delete(request, pk):
    cast_member = get_object_or_404(Cast, pk=pk)
    cast_member.delete()
    return Response({'message': 'Cast deleted successfully!'}, status=status.HTTP_200_OK)

# 6. Cast All Delete
@api_view(['DELETE'])
def cast_all_delete(request):
    count = Cast.objects.all().count()
    Cast.objects.all().delete()
    return Response(
        {'message': f'Total {count} casts deleted successfully!'}, 
        status=status.HTTP_200_OK
    )