from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import Movie, Series, Favorite

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite_manager(request):
    user = request.user 

    # --- 1. Get Favorite List (GET) ---
    if request.method == 'GET':
        try:
            favorites = Favorite.objects.filter(user=user).order_by('-created_at')
            data = []
            
            for fav in favorites:
                if not fav.movie and not fav.series:
                    continue

                item = {
                    "id": fav.id,
                    "movie": fav.movie.id if fav.movie else None,
                    "series": fav.series.id if fav.series else None,
                    "movie_details": None,
                    "series_details": None
                }

                # Movie Details
                if fav.movie:
                    # ✅ Rating Object ဖြစ်နေရင် စာသားပြောင်းပေးဖို့ လိုတယ်
                    movie_rating = "0.0"
                    if fav.movie.rating:
                        # တကယ်လို့ Rating model မှာ field နာမည်က name ဆိုရင် .name လို့သုံးပါ
                        # ဥပမာ - fav.movie.rating.name သို့မဟုတ် str(fav.movie.rating)
                        movie_rating = str(fav.movie.rating) 

                    item["movie_details"] = {
                        "id": fav.movie.id,
                        "title": fav.movie.title,
                        "poster": fav.movie.poster.url if fav.movie.poster else None,
                        "rating": movie_rating,
                    }

                # Series Details
                if fav.series:
                    series_rating = "0.0"
                    if fav.series.rating:
                        series_rating = str(fav.series.rating)

                    item["series_details"] = {
                        "id": fav.series.id,
                        "title": fav.series.title,
                        "poster": fav.series.poster.url if fav.series.poster else None,
                        "rating": series_rating,
                    }
                
                data.append(item)
                
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"🔥 JSON Error Fix Check: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- 2. Add Favorite (POST) ---
    elif request.method == 'POST':
        movie_id = request.data.get('movie')
        series_id = request.data.get('series')
        try:
            if movie_id:
                movie_obj = Movie.objects.get(pk=movie_id)
                fav, created = Favorite.objects.get_or_create(user=user, movie=movie_obj)
            elif series_id:
                series_obj = Series.objects.get(pk=series_id)
                fav, created = Favorite.objects.get_or_create(user=user, series=series_obj)
            else:
                return Response({"error": "ID required"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Success"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # --- 3. Remove Favorite (DELETE) ---
    elif request.method == 'DELETE':
        movie_id = request.data.get('movie')
        series_id = request.data.get('series')
        if movie_id:
            Favorite.objects.filter(user=user, movie_id=movie_id).delete()
        elif series_id:
            Favorite.objects.filter(user=user, series_id=series_id).delete()
        return Response({"message": "Removed"}, status=status.HTTP_204_NO_CONTENT)