from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import HeroSection
from ..serializers import HeroSectionSerializer

# 1. Banner List with Pagination
@api_view(['GET'])
def banner_list(request):
    """
    Hero Sections (Banners) အားလုံးကို DRF Pagination သုံးပြီး ပြသခြင်း
    """
    banners = HeroSection.objects.all().order_by('-created_at')
    
    paginator = PageNumberPagination()
    paginator.page_size = 2
    
    result_page = paginator.paginate_queryset(banners, request)
    serializer = HeroSectionSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# 2. Banner Create
@api_view(['POST'])
def banner_create(request):
    serializer = HeroSectionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Banner Detail
@api_view(['GET'])
def banner_detail(request, pk):
    # UUID pk ကိုသုံးပြီး ရှာဖွေခြင်း
    banner = get_object_or_404(HeroSection, pk=pk)
    serializer = HeroSectionSerializer(banner)
    return Response(serializer.data)

# 4. Banner Full Update (UUID Based)
@api_view(['PUT'])
def banner_update(request, pk):
    """
    UUID ကိုအသုံးပြု၍ Hero Section တစ်ခုလုံးကို Full Update လုပ်ခြင်း
    (Required fields အားလုံး ပို့ပေးရန် လိုအပ်သည်)
    """
    banner = get_object_or_404(HeroSection, pk=pk)
    
    # partial=True ကို ဖြုတ်လိုက်ခြင်းဖြင့် Full Update ဖြစ်သွားပါပြီ
    serializer = HeroSectionSerializer(banner, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 5. Banner Delete
@api_view(['DELETE'])
def banner_delete(request, pk):
    banner = get_object_or_404(HeroSection, pk=pk)
    banner.delete()
    return Response({'message': 'Deleted successfully'}, status=status.HTTP_200_OK)

# 6. Banner All Delete
@api_view(['DELETE'])
def banner_all_delete(request):
    HeroSection.objects.all().delete()
    # HTTP_200_OK သို့ ပြောင်းပါ
    return Response({'message': 'All banners deleted!'}, status=status.HTTP_200_OK)