from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Director
from ..serializers import DirectorSerializer

# 1. Director List with Pagination
@api_view(['GET'])
def director_list(request):
    """
    ဒါရိုက်တာအားလုံးကို Pagination ဖြင့် ပြသခြင်း
    """
    directors = Director.objects.all().order_by('director')
    
    paginator = PageNumberPagination()
    paginator.page_size = 10
    
    result_page = paginator.paginate_queryset(directors, request)
    serializer = DirectorSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# 2. Director Create
@api_view(['POST'])
def director_create(request):
    """
    ဒါရိုက်တာအသစ် ထည့်သွင်းခြင်း (Image ပါလျှင် form-data သုံးပါ)
    """
    serializer = DirectorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Director Detail
@api_view(['GET'])
def director_detail(request, pk):
    director = get_object_or_404(Director, pk=pk)
    serializer = DirectorSerializer(director)
    return Response(serializer.data)

# 4. Director Full Update
@api_view(['PUT'])
def director_update(request, pk):
    """
    ဒါရိုက်တာအချက်အလက်ကို Full Update လုပ်ခြင်း
    """
    director = get_object_or_404(Director, pk=pk)
    serializer = DirectorSerializer(director, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 5. Director Delete
@api_view(['DELETE'])
def director_delete(request, pk):
    director = get_object_or_404(Director, pk=pk)
    director.delete()
    return Response({'message': 'Director deleted successfully!'}, status=status.HTTP_200_OK)

# 6. Director All Delete
@api_view(['DELETE'])
def director_all_delete(request):
    count = Director.objects.all().count()
    Director.objects.all().delete()
    return Response(
        {'message': f'Total {count} directors deleted successfully!'}, 
        status=status.HTTP_200_OK
    )