from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import Movie, Series, Favorite

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite_manager(request):
    # request.user ကနေ လက်ရှိ Login ဝင်ထားတဲ့ User Object ကို ယူမယ်
    user = request.user 

    # --- 1. Get Favorite List (GET Method) ---
    if request.method == 'GET':
        favorites = Favorite.objects.filter(user=user).order_by('-created_at')
        
        data = []
        for fav in favorites:
            # Movie သို့မဟုတ် Series တစ်ခုခု ရှိနေရင် Data ထည့်မယ်
            item = {
                "id": fav.id,
                "movie": fav.movie.id if fav.movie else None,
                "series": fav.series.id if fav.series else None,
                "movie_details": {
                    "id": fav.movie.id,
                    "title": fav.movie.title,
                    "poster": fav.movie.poster.url if fav.movie and fav.movie.poster else None,
                    "rating": fav.movie.rating if hasattr(fav.movie, 'rating') else None,
                } if fav.movie else None,
                "series_details": {
                    "id": fav.series.id,
                    "title": fav.series.title,
                    "poster": fav.series.poster.url if fav.series and fav.series.poster else None,
                    "rating": fav.series.rating if hasattr(fav.series, 'rating') else None,
                } if fav.series else None
            }
            data.append(item)
            
        return Response(data, status=status.HTTP_200_OK)

    # --- 2. Add Favorite (POST Method) ---
    elif request.method == 'POST':
        movie_id = request.data.get('movie')
        series_id = request.data.get('series')

        try:
            if movie_id:
                movie_obj = Movie.objects.get(id=movie_id)
                # get_or_create သုံးရင် duplicate မဖြစ်အောင် Django က ကြည့်ပေးတယ်
                fav, created = Favorite.objects.get_or_create(user=user, movie=movie_obj)
            elif series_id:
                series_obj = Series.objects.get(id=series_id)
                fav, created = Favorite.objects.get_or_create(user=user, series=series_obj)
            else:
                return Response({"error": "Movie or Series ID required"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Added to favorites"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # --- 3. Remove Favorite (DELETE Method) ---
    elif request.method == 'DELETE':
        movie_id = request.data.get('movie')
        series_id = request.data.get('series')

        if movie_id:
            Favorite.objects.filter(user=user, movie_id=movie_id).delete()
        elif series_id:
            Favorite.objects.filter(user=user, series_id=series_id).delete()
            
        return Response({"message": "Removed from favorites"}, status=status.HTTP_204_NO_CONTENT)