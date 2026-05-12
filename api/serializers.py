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

from rest_framework import serializers
from .models import Movie, Country, Genre, Director, Cast, Premiere, Rating

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


from rest_framework import serializers
from .models import Movie, MovieVideo, Genre, Country, Rating, Premiere, Director, Cast

class MovieVideoSerializer(serializers.ModelSerializer):
    # App UI မှာ သုံးဖို့ 
    play_url = serializers.ReadOnlyField(source='embed_url')
    
    class Meta:
        model = MovieVideo
        fields = ['id', 'quality', 'play_url', 'file_size', 'duration', 'thumbnail_url']

class MovieSerializer(serializers.ModelSerializer):
    videos = MovieVideoSerializer(many=True, read_only=True)
    genres = serializers.StringRelatedField(many=True)
    country = serializers.StringRelatedField()
    rating = serializers.StringRelatedField()
    release_year = serializers.StringRelatedField()
    directors = serializers.StringRelatedField(many=True)
    casts = serializers.StringRelatedField(many=True)

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'slug', 'description', 'poster', 
            'country', 'rating', 'release_year', 'genres', 
            'directors', 'casts', 'is_trending', 'view_count', 
            'videos', 'created_at'
        ]


class MovieListSerializer(serializers.ModelSerializer):
    # Detail မှာ သုံးသလိုမျိုး Field တွေ အကုန်ဒီမှာ ကြေညာပေးရပါမယ်
    videos = MovieVideoSerializer(many=True, read_only=True)
    genres = serializers.StringRelatedField(many=True)
    country = serializers.StringRelatedField()
    rating = serializers.StringRelatedField()
    release_year = serializers.StringRelatedField()
    directors = serializers.StringRelatedField(many=True)
    casts = serializers.StringRelatedField(many=True)

    class Meta:
        model = Movie
        # List မှာလည်း Detail ကလို Field တွေ အကုန်ပြခိုင်းလိုက်တာပါ
        fields = [
            'id', 'title', 'slug', 'description', 'poster', 
            'country', 'rating', 'release_year', 'genres', 
            'directors', 'casts', 'is_trending', 'view_count', 
            'videos', 'created_at'
        ]