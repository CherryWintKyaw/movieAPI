from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Favorite
from ..serializers import FavoriteListSerializer, FavoriteActionSerializer

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite_manager(request):
    user = request.user

    # --- ၁။ Favorite စာရင်းကြည့်ရန် (GET) ---
    if request.method == 'GET':
        favorites = Favorite.objects.filter(user=user).order_by('-created_at')
        serializer = FavoriteListSerializer(favorites, many=True)
        return Response(serializer.data)

    # --- ၂။ Favorite အသစ်ထည့်ရန် (POST) ---
    elif request.method == 'POST':
        serializer = FavoriteActionSerializer(data=request.data)
        if serializer.is_valid():
            movie_id = serializer.validated_data.get('movie')
            series_id = serializer.validated_data.get('series')

            # ရှိပြီးသားလား စစ်ဆေးခြင်း
            if Favorite.objects.filter(user=user, movie=movie_id, series=series_id).exists():
                return Response({"detail": "ရှိပြီးသားဖြစ်သည်"}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- ၃။ Favorite ပြန်ဖြုတ်ရန် (DELETE) ---
    elif request.method == 'DELETE':
        movie_id = request.data.get('movie')
        series_id = request.data.get('series')

        favorite_item = Favorite.objects.filter(user=user, movie_id=movie_id, series_id=series_id).first()
        
        if favorite_item:
            favorite_item.delete()
            return Response({"detail": "ဖယ်ရှားပြီးပါပြီ"}, status=status.HTTP_204_NO_CONTENT)
        
        return Response({"detail": "ရှာမတွေ့ပါ"}, status=status.HTTP_404_NOT_FOUND)