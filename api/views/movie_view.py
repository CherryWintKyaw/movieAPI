from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Movie
from ..serializers import MovieSerializer

# 1. Movie List with Pagination
@api_view(['GET'])
def movie_list(request):
    """
    ရုပ်ရှင်အားလုံးကို Pagination ဖြင့် ပြသခြင်း (နောက်ဆုံးတင်တာ အရင်ပြမည်)
    """
    movies = Movie.objects.all().order_by('-created_at')
    
    paginator = PageNumberPagination()
    paginator.page_size = 10
    
    result_page = paginator.paginate_queryset(movies, request)
    serializer = MovieSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# 2. Movie Create
@api_view(['POST'])
def movie_create(request):
    """
    ရုပ်ရှင်အသစ် ထည့်သွင်းခြင်း
    (Poster အတွက် form-data သုံးရန်နှင့် Master Data များအတွက် UUID ပို့ရန်)
    """
    serializer = MovieSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Movie Detail
@api_view(['GET'])
def movie_detail(request, pk):
    """
    UUID pk သို့မဟုတ် slug ဖြင့် ကြည့်နိုင်ရန် (pk ကို ဦးစားပေးထားသည်)
    """
    movie = get_object_or_404(Movie, pk=pk)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)

# 4. Movie Full Update
@api_view(['PUT'])
def movie_update(request, pk):
    """
    ရုပ်ရှင်အချက်အလက်ကို Full Update လုပ်ခြင်း
    """
    movie = get_object_or_404(Movie, pk=pk)
    serializer = MovieSerializer(movie, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 5. Movie Delete
@api_view(['DELETE'])
def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    return Response({'message': 'Movie deleted successfully!'}, status=status.HTTP_200_OK)

# 6. Movie All Delete
@api_view(['DELETE'])
def movie_all_delete(request):
    count = Movie.objects.all().count()
    Movie.objects.all().delete()
    return Response(
        {'message': f'Total {count} movies deleted successfully!'}, 
        status=status.HTTP_200_OK
    )