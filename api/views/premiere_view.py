from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Premiere
from ..serializers import PremiereSerializer

# 1. Premiere List with Pagination
@api_view(['GET'])
def premiere_list(request):
    """
    ခုနှစ်စာရင်းအားလုံးကို Pagination ဖြင့် ပြသခြင်း (အသစ်ဆုံးကို အပေါ်ကပြမည်)
    """
    years = Premiere.objects.all().order_by('-year')
    
    paginator = PageNumberPagination()
    paginator.page_size = 10
    
    result_page = paginator.paginate_queryset(years, request)
    serializer = PremiereSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# 2. Premiere Create
@api_view(['POST'])
def premiere_create(request):
    """
    ခုနှစ်အသစ် ထည့်သွင်းခြင်း
    """
    serializer = PremiereSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Premiere Detail
@api_view(['GET'])
def premiere_detail(request, pk):
    year_entry = get_object_or_404(Premiere, pk=pk)
    serializer = PremiereSerializer(year_entry)
    return Response(serializer.data)

# 4. Premiere Full Update
@api_view(['PUT'])
def premiere_update(request, pk):
    """
    ခုနှစ်အချက်အလက်ကို Full Update လုပ်ခြင်း
    """
    year_entry = get_object_or_404(Premiere, pk=pk)
    serializer = PremiereSerializer(year_entry, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 5. Premiere Delete
@api_view(['DELETE'])
def premiere_delete(request, pk):
    year_entry = get_object_or_404(Premiere, pk=pk)
    year_entry.delete()
    return Response({'message': 'Premiere year deleted successfully!'}, status=status.HTTP_200_OK)

# 6. Premiere All Delete
@api_view(['DELETE'])
def premiere_all_delete(request):
    count = Premiere.objects.all().count()
    Premiere.objects.all().delete()
    return Response(
        {'message': f'Total {count} premiere years deleted successfully!'}, 
        status=status.HTTP_200_OK
    )