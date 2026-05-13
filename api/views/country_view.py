from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Country
from ..serializers import CountrySerializer
from django.db.models import Q

# 1. Country List with Pagination
@api_view(['GET'])
def country_list(request):
    """
    နိုင်ငံစာရင်းများကို ID (UUID) သို့မဟုတ် နိုင်ငံအမည်ဖြင့် 
    Search လုပ်နိုင်ပြီး Pagination ဖြင့် ပြသခြင်း
    """
    # 1. နိုင်ငံအားလုံးကို အက္ခရာစဉ်အလိုက် ယူမယ်
    countries = Country.objects.all().order_by('country')
    
    # 2. Search Logic (ID နှင့် Country Field အားလုံးကို ရှာဖွေခြင်း)
    search_query = request.query_params.get('search', None)
    if search_query:
        countries = countries.filter(
            Q(id__icontains=search_query) | # UUID ID ကို ရှာမယ်
            Q(country__icontains=search_query) # နိုင်ငံအမည်ကို ရှာမယ်
        ).distinct()

    # 3. Pagination သတ်မှတ်မယ် (တစ်မျက်နှာလျှင် ၁၀ ခု)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    
    # 4. Result ကို Serialize လုပ်ပြီး ပြန်ပေးမယ်
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
    # ၁။ ပေးထားတဲ့ UUID နဲ့ data ရှိမရှိအရင်ရှာမယ်၊ မရှိရင် 404 ပြမယ်
    country = get_object_or_404(Country, pk=pk)
    
    # ၂။ လက်ရှိ object ထဲကို request ကလာတဲ့ data အသစ်တွေ ထည့်ပေးမယ်
    # unique=True စစ်ဆေးတာကို serializer.is_valid() က လုပ်ဆောင်ပေးသွားမှာပါ
    serializer = CountrySerializer(country, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # ၃။ Validation error (ဥပမာ- နာမည်တူနေတာမျိုး) ရှိရင် error ပြန်ပို့မယ်
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