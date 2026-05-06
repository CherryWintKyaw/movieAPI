from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Country
from ..serializers import CountrySerializer

# 1. Country List with Pagination
@api_view(['GET'])
def country_list(request):
    """
    နိုင်ငံစာရင်းအားလုံးကို Pagination ဖြင့် ပြသခြင်း
    """
    countries = Country.objects.all().order_by('country')
    
    paginator = PageNumberPagination()
    paginator.page_size = 10  # တစ်မျက်နှာလျှင် ၁၀ ခုစီပြသမည်
    
    result_page = paginator.paginate_queryset(countries, request)
    serializer = CountrySerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# 2. Country Create
@api_view(['POST'])
def country_create(request):
    """
    နိုင်ငံအသစ် ထည့်သွင်းခြင်း
    """
    serializer = CountrySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Country Detail
@api_view(['GET'])
def country_detail(request, pk):
    """
    UUID pk ဖြင့် နိုင်ငံတစ်ခု၏ အချက်အလက်ကို ကြည့်ရှုခြင်း
    """
    country = get_object_or_404(Country, pk=pk)
    serializer = CountrySerializer(country)
    return Response(serializer.data)

# 4. Country Full Update
@api_view(['PUT'])
def country_update(request, pk):
    """
    နိုင်ငံအချက်အလက်ကို Full Update လုပ်ခြင်း
    """
    country = get_object_or_404(Country, pk=pk)
    # partial=False (Default) ဖြစ်သောကြောင့် Full Update ဖြစ်သည်
    serializer = CountrySerializer(country, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 5. Country Delete
@api_view(['DELETE'])
def country_delete(request, pk):
    """
    နိုင်ငံတစ်ခုကို ဖျက်ထုတ်ခြင်း
    """
    country = get_object_or_404(Country, pk=pk)
    country.delete()
    return Response({'message': 'Country deleted successfully!'}, status=status.HTTP_200_OK)

# 6. Country All Delete
@api_view(['DELETE'])
def country_all_delete(request):
    """
    နိုင်ငံများအားလုံးကို တစ်ခါတည်း ဖျက်ထုတ်ခြင်း
    """
    count = Country.objects.all().count()
    Country.objects.all().delete()
    return Response(
        {'message': f'Total {count} countries deleted successfully!'}, 
        status=status.HTTP_200_OK
    )