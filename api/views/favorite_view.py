from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import Movie, Series, Favorite
from api.serializers import FavoriteSerializer # Serializer ရှိတယ်လို့ ယူဆထားပါတယ်

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated]) # Token ပါမှ ဝင်လို့ရအောင် ပိတ်ထားမယ်
def favorite_manager(request):
    # ✅ request.user သည် User Instance အစစ် ဖြစ်ရပါမယ်
    user = request.user 

    # --- 1. Get Favorite List ---
    if request.method == 'GET':
        # အခု ဒီ line မှာ admin@gmail.com ဖြစ်နေတဲ့ error ပျောက်သွားပါပြီ
        favorites = Favorite.objects.filter(user=user).order_by('-created_at')
        
        # serializer မသုံးချင်ရင် manual data ဆောက်လို့ရပါတယ်
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

    # --- 2. Add Favorite (POST) ---
    elif request.method == 'POST':
        movie_id = request.data.get('movie')
        series_id = request.data.get('series')

        if movie_id:
            movie = Movie.objects.get(id=movie_id)
            fav, created = Favorite.objects.get_or_create(user=user, movie=movie)
        elif series_id:
            series = Series.objects.get(id=series_id)
            fav, created = Favorite.objects.get_or_create(user=user, series=series)
        else:
            return Response({"error": "Movie or Series ID required"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Added to favorites"}, status=status.HTTP_201_CREATED)

    # --- 3. Remove Favorite (DELETE) ---
    elif request.method == 'DELETE':
        movie_id = request.data.get('movie')
        series_id = request.data.get('series')

        if movie_id:
            Favorite.objects.filter(user=user, movie_id=movie_id).delete()
        elif series_id:
            Favorite.objects.filter(user=user, series_id=series_id).delete()
            
        return Response({"message": "Removed from favorites"}, status=status.HTTP_204_NO_CONTENT)