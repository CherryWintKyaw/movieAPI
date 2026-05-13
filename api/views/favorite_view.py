from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import Movie, Series, Favorite
from api.serializers import FavoriteSerializer 

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite_manager(request):
    user = request.user 

    # --- 1. Get List ---
    if request.method == 'GET':
        favorites = Favorite.objects.filter(user=user).order_by('-created_at')
        data = []
        for fav in favorites:
            item = {
                "id": fav.id,
                "movie": fav.movie.id if fav.movie else None,
                "series": fav.series.id if fav.series else None,
                "movie_details": {
                    "id": fav.movie.id,
                    "title": fav.movie.title,
                    "poster": fav.movie.poster.url if fav.movie and fav.movie.poster else None,
                    "rating": fav.movie.rating,
                } if fav.movie else None,
                "series_details": {
                    "id": fav.series.id,
                    "title": fav.series.title,
                    "poster": fav.series.poster.url if fav.series and fav.series.poster else None,
                    "rating": fav.series.rating,
                } if fav.series else None
            }
            data.append(item)
        return Response(data, status=status.HTTP_200_OK)

    # --- 2. Add (POST) ---
    elif request.method == 'POST':
        serializer = FavoriteSerializer(data=request.data)
        if serializer.is_valid():
            # user ကို လက်ရှိ login ဝင်ထားသူနဲ့ manual တွဲပေးရမယ်
            serializer.save(user=user)
            return Response({"message": "Added to favorites"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- 3. Remove (DELETE) ---
    elif request.method == 'DELETE':
        movie_id = request.data.get('movie')
        series_id = request.data.get('series')
        
        if movie_id:
            Favorite.objects.filter(user=user, movie_id=movie_id).delete()
        elif series_id:
            Favorite.objects.filter(user=user, series_id=series_id).delete()
            
        return Response({"message": "Removed"}, status=status.HTTP_204_NO_CONTENT)