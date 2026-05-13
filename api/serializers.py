from rest_framework import serializers
from .models import *

class HeroSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSection
        # Fields အားလုံးကို ဖော်ပြထားပါတယ်
        # id က UUID field အနေနဲ့ အလိုအလျောက် အလုပ်လုပ်ပါလိမ့်မယ်
        fields = [
            'id', 
            'title', 
            'rating', 
            'description', 
            'button_text', 
            'link', 
            'image', 
            'created_at',
            'updated_at'
        ]
        
        # id, created_at နဲ့ updated_at တို့ကို read_only ပေးထားတာ ပိုစိတ်ချရပါတယ်
        read_only_fields = ['id', 'created_at', 'updated_at']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class CastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cast
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class PremiereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Premiere
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# Master Data Serializers (ချိတ်ဆက်ထားတဲ့ Model များအတွက်)
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'country']

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'genre']

class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = ['id', 'director', 'image']

class CastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cast
        fields = ['id', 'cast', 'image']

class PremiereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Premiere
        fields = ['id', 'year']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'rating']


class MovieVideoSerializer(serializers.ModelSerializer):
    play_url = serializers.ReadOnlyField(source='embed_url')
    
    class Meta:
        model = MovieVideo
        # thumbnail_url ကို ဖြုတ်လိုက်ပါပြီ
        fields = ['id', 'quality', 'play_url', 'file_size', 'duration']

class MovieSerializer(serializers.ModelSerializer):
    videos = MovieVideoSerializer(many=True, read_only=True)
    directors = DirectorSerializer(many=True, read_only=True)
    casts = CastSerializer(many=True, read_only=True)
    
    # POST/PUT အတွက် ID လက်ခံဖို့ ထားထားမယ်
    genres = serializers.PrimaryKeyRelatedField(many=True, queryset=Genre.objects.all())
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())
    rating = serializers.PrimaryKeyRelatedField(queryset=Rating.objects.all())
    release_year = serializers.PrimaryKeyRelatedField(queryset=Premiere.objects.all())

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'slug', 'description', 'poster', 
            'country', 'rating', 'release_year', 'genres', 
            'directors', 'casts', 'is_trending', 'view_count', 
            'videos', 'created_at'
        ]

    # ✅ ဒီအပိုင်းကို ထည့်ပေးပါ (ဒေတာ ပြန်ထုတ်ပေးတဲ့အခါ နာမည်ပြောင်းပေးတာ)
    def to_representation(self, instance):
        response = super().to_representation(instance)
        # Rating နာမည်ပြောင်းမယ် (မင်းရဲ့ model field name က 'rating' ဖြစ်မယ်လို့ ယူဆပါတယ်)
        if instance.rating:
            response['rating'] = str(instance.rating) 
        
        # Release Year နာမည်ပြောင်းမယ်
        if instance.release_year:
            response['release_year'] = str(instance.release_year)
            
        # Country နာမည်ပြောင်းမယ်
        if instance.country:
            response['country'] = str(instance.country)

        # Genres ကို နာမည် list အနေနဲ့ ပြောင်းမယ်
        response['genres'] = [str(genre) for genre in instance.genres.all()]
        
        return response
    #series

# ၁။ Episode Detail Serializer (Episode အချက်အလက်သီးသန့်)
class EpisodeDetailSerializer(serializers.ModelSerializer):
    play_url = serializers.ReadOnlyField(source='embed_url')

    class Meta:
        model = Episode
        fields = [
            'id', 'episode_number', 'title', 
            'dood_file_code', 'play_url', 'file_size', 
            'duration', 'view_count', 'created_at'
        ]

# ၂။ Season Detail Serializer (Episodes တွေကိုပါ တစ်ခါတည်း ဆွဲထုတ်မယ်)
class SeasonDetailSerializer(serializers.ModelSerializer):
    episodes = EpisodeDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = ['id', 'season_number', 'description', 'episodes', 'created_at']

# ၃။ Main Series Serializer (Seasons/Episodes အကုန်လုံး အဆင့်ဆင့် ပြန်ချိတ်မယ်)
class SeriesSerializer(serializers.ModelSerializer):
    # Nested Relation: Seasons တွေကို အစုံအလင် ပြန်ပြမယ်
    seasons = SeasonDetailSerializer(many=True, read_only=True)
    
    # POST/PUT အတွက် ID လက်ခံရန်
    genres = serializers.PrimaryKeyRelatedField(many=True, queryset=Genre.objects.all())
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), allow_null=True)
    rating = serializers.PrimaryKeyRelatedField(queryset=Rating.objects.all(), allow_null=True)
    release_year = serializers.PrimaryKeyRelatedField(queryset=Premiere.objects.all(), allow_null=True)

    class Meta:
        model = Series
        fields = [
            'id', 'title', 'slug', 'description', 'poster', 
            'country', 'rating', 'release_year', 'genres', 
            'directors', 'casts', 'is_trending', 'view_count', 
            'seasons', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        
        # Foreign Key Object များကို String နာမည်များအဖြစ် ပြောင်းလဲခြင်း
        if instance.country: response['country'] = str(instance.country)
        if instance.rating: response['rating'] = str(instance.rating)
        if instance.release_year: response['release_year'] = str(instance.release_year)
        
        # Many-to-Many Fields ကို Custom ပြုလုပ်ခြင်း
        response['genres'] = [str(genre) for genre in instance.genres.all()]
        response['directors'] = DirectorSerializer(instance.directors.all(), many=True, context=self.context).data
        response['casts'] = CastSerializer(instance.casts.all(), many=True, context=self.context).data
        
        return response

# ၄။ တစ်သီးပုဂ္ဂလ CRUD အတွက် Season Serializer
class SeasonSerializer(serializers.ModelSerializer):
    series = serializers.PrimaryKeyRelatedField(queryset=Series.objects.all())

    class Meta:
        model = Season
        fields = ['id', 'series', 'season_number', 'description', 'created_at']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.series:
            response['series_name'] = instance.series.title
            response['series'] = instance.series.title
        return response

    def validate(self, data):
        series = data.get('series')
        season_number = data.get('season_number')
        if Season.objects.filter(series=series, season_number=season_number).exists():
            if not self.instance or self.instance.season_number != season_number:
                raise serializers.ValidationError(f"Season {season_number} for this series already exists.")
        return data

# ၅။ တစ်သီးပုဂ္ဂလ CRUD အတွက် Episode Serializer
class EpisodeSerializer(serializers.ModelSerializer):
    season = serializers.PrimaryKeyRelatedField(queryset=Season.objects.all())
    play_url = serializers.ReadOnlyField(source='embed_url')

    class Meta:
        model = Episode
        fields = [
            'id', 'season', 'episode_number', 'title', 
            'dood_file_code', 'play_url', 'file_size', 'duration', 
            'view_count', 'created_at'
        ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.season:
            response['series_title'] = instance.season.series.title
            response['season_number'] = instance.season.season_number
            response['season'] = f"Season {instance.season.season_number}"
        return response
    



# --- ၁။ Favorite List ပြတဲ့အခါ သုံးဖို့ (Nested Data ပါမယ်) ---
class FavoriteListSerializer(serializers.ModelSerializer):
    # Movie နဲ့ Series ရဲ့ title နဲ့ poster ကိုပါ တစ်ခါတည်း ပြချင်ရင် သုံးဖို့
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    movie_poster = serializers.ImageField(source='movie.poster', read_only=True)
    series_title = serializers.CharField(source='series.title', read_only=True)
    series_poster = serializers.ImageField(source='series.poster', read_only=True)

    class Meta:
        model = Favorite
        fields = [
            'id', 'user', 'movie', 'movie_title', 'movie_poster', 
            'series', 'series_title', 'series_poster', 'created_at'
        ]

# --- ၂။ Favorite လုပ်တဲ့အခါ (Add/Remove) သုံးဖို့ ---
# ⚠️ ဒီနေရာမှာ နာမည်ကို "FavoriteSerializer" လို့ပဲ ပေးရပါမယ်
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'movie', 'series']
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def validate(self, attrs):
        movie = attrs.get('movie')
        series = attrs.get('series')
        if not movie and not series:
            raise serializers.ValidationError("Movie သို့မဟုတ် Series တစ်ခုခု ရွေးပေးရပါမယ်။")
        if movie and series:
            raise serializers.ValidationError("Movie နဲ့ Series နှစ်ခုလုံး တစ်ပြိုင်တည်း Favorite လုပ်လို့မရပါ။")
        return attrs
    
class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ['id', 'fcm_token', 'device_type', 'created_at']
        extra_kwargs = {
            # Token ရှိပြီးသားဆိုရင် Serializer ကနေ Error မပြအောင် validator ကို ပိတ်ထားတာပါ
            'fcm_token': {'validators': []} 
        }

    # Serializer ထဲမှာ create method ထပ်ရေးစရာ မလိုတော့ဘူး (View ထဲမှာ ရေးမှာမို့လို့)