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


# api/serializers.py

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
    
    # Use PrimaryKeyRelatedField so you can send ID numbers in your POST request
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