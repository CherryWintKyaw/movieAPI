from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import Movie, Series, Favorite

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite_manager(request):
    user = request.user 

    # --- 1. Get Favorite List ---
    if request.method == 'GET':
        try:
            # လက်ရှိ User နဲ့ဆိုင်တဲ့ Favorites တွေကို အသစ်ဆုံးကနေ အရင်ယူမယ်
            favorites = Favorite.objects.filter(user=user).order_by('-created_at')
            
            data = []
            for fav in favorites:
                # Security Check: Movie ရော Series ရော null ဖြစ်နေတဲ့ row မျိုးဆိုရင် ကျော်သွားမယ်
                if not fav.movie and not fav.series:
                    continue

                item = {
                    "id": fav.id,
                    "movie": fav.movie.id if fav.movie else None,
                    "series": fav.series.id if fav.series else None,
                    "movie_details": None,
                    "series_details": None
                }

                # Movie Details ရှိရင် ထည့်မယ်
                if fav.movie:
                    item["movie_details"] = {
                        "id": fav.movie.id,
                        "title": fav.movie.title,
                        "poster": fav.movie.poster.url if fav.movie.poster else None,
                        "rating": getattr(fav.movie, 'rating', "0.0"),
                    }

                # Series Details ရှိရင် ထည့်မယ်
                if fav.series:
                    item["series_details"] = {
                        "id": fav.series.id,
                        "title": fav.series.title,
                        "poster": fav.series.poster.url if fav.series.poster else None,
                        "rating": getattr(fav.series, 'rating', "0.0"),
                    }
                
                data.append(item)
                
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Error တက်ရင် Terminal မှာ ဘာကြောင့်လဲဆိုတာ မြင်ရအောင် print ထုတ်ပေးပါ
            print(f"🔥 GET Favorite Error: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- 2. Add Favorite (POST) ---
    elif request.method == 'POST':
        movie_id = request.data.get('movie')
        series_id = request.data.get('series')

        try:
            if movie_id:
                movie_obj = Movie.objects.get(id=movie_id)
                fav, created = Favorite.objects.get_or_create(user=user, movie=movie_obj)
            elif series_id:
                series_obj = Series.objects.get(id=series_id)
                fav, created = Favorite.objects.get_or_create(user=user, series=series_obj)
            else:
                return Response({"error": "Movie or Series ID required"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Added to favorites"}, status=status.HTTP_201_CREATED)
        except (Movie.DoesNotExist, Series.DoesNotExist):
            return Response({"error": "Content not found"}, status=status.HTTP_404_NOT_FOUND)
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
            
        return Response({"message": "Removed from favorites"}, status=status.HTTP_204_NO_CONTENT)