from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Genre
from ..serializers import GenreSerializer
from django.db.models import Q

# 1. Genre List with Pagination
@api_view(['GET'])
def genre_list(request):
    """
    ရုပ်ရှင်အမျိုးအစား (Genre) များကို ID (UUID) သို့မဟုတ် နာမည်ဖြင့် 
    Search လုပ်နိုင်ပြီး Pagination ဖြင့် ပြသခြင်း
    """
    # 1. Genre အားလုံးကို အက္ခရာစဉ်အလိုက် ယူမယ်
    genres = Genre.objects.all().order_by('genre')
    
    # 2. Search Logic (ID နှင့် Genre Field အားလုံးကို ရှာဖွေခြင်း)
    search_query = request.query_params.get('search', None)
    if search_query:
        genres = genres.filter(
            Q(id__icontains=search_query) | # UUID ID ကို ရှာမယ်
            Q(genre__icontains=search_query) # Genre နာမည် (Action, Comedy, etc.) ကို ရှာမယ်
        ).distinct()

    # 3. Pagination သတ်မှတ်မယ် (တစ်မျက်နှာလျှင် ၁၀ ခု)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    
    # 4. Result ကို Serialize လုပ်ပြီး ပြန်ပေးမယ်
    result_page = paginator.paginate_queryset(genres, request)
    serializer = GenreSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# 2. Genre Create
@api_view(['POST'])
def genre_create(request):
    """
    Genre အသစ် ထည့်သွင်းခြင်း
    """
    serializer = GenreSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Genre Detail
@api_view(['GET'])
def genre_detail(request, pk):
    """
    UUID pk ဖြင့် Genre တစ်ခုချင်းစီ၏ အချက်အလက်ကို ကြည့်ရှုခြင်း
    """
    genre = get_object_or_404(Genre, pk=pk)
    serializer = GenreSerializer(genre)
    return Response(serializer.data)

# 4. Genre Full Update
@api_view(['PUT'])
def genre_update(request, pk):
    """
    Genre အချက်အလက်ကို Full Update လုပ်ခြင်း
    """
    genre = get_object_or_404(Genre, pk=pk)
    # PUT method ဖြစ်သောကြောင့် partial=True မသုံးပါ (Full Update)
    serializer = GenreSerializer(genre, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 5. Genre Delete
@api_view(['DELETE'])
def genre_delete(request, pk):
    """
    Genre တစ်ခုကို ဖျက်ထုတ်ခြင်း
    """
    genre = get_object_or_404(Genre, pk=pk)
    genre.delete()
    return Response({'message': 'Genre deleted successfully!'}, status=status.HTTP_200_OK)

# 6. Genre All Delete
@api_view(['DELETE'])
def genre_all_delete(request):
    """
    Genre များအားလုံးကို တစ်ခါတည်း ဖျက်ထုတ်ခြင်း
    """
    count = Genre.objects.all().count()
    Genre.objects.all().delete()
    return Response(
        {'message': f'Total {count} genres deleted successfully!'}, 
        status=status.HTTP_200_OK
    )