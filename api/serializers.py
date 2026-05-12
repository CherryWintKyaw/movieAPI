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

class SeriesSerializer(serializers.ModelSerializer):
    # POST/PUT အတွက် ID လက်ခံရန် PrimaryKeyRelatedField သုံးမည်
    genres = serializers.PrimaryKeyRelatedField(many=True, queryset=Genre.objects.all())
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())
    rating = serializers.PrimaryKeyRelatedField(queryset=Rating.objects.all())
    release_year = serializers.PrimaryKeyRelatedField(queryset=Premiere.objects.all())

    class Meta:
        model = Series
        fields = '__all__'
        read_only_fields = ['slug']

    # Title ရှိပြီးသားလားလို့ API ကနေ စစ်ပေးမယ့် function
    def validate_title(self, value):
        if Series.objects.filter(title__iexact=value).exists():
            raise serializers.ValidationError("A series with this title already exists.")
        return value

    def to_representation(self, instance):
        """
        Data ပြန်ထုတ်ပေးတဲ့အခါ ID တွေအစား နာမည်တွေ ပြောင်းပေးတာ
        """
        response = super().to_representation(instance)
        
        # Foreign Key Fields များကို String အဖြစ်ပြောင်းလဲခြင်း
        if instance.rating:
            response['rating'] = str(instance.rating)
        
        if instance.release_year:
            response['release_year'] = str(instance.release_year)
            
        if instance.country:
            response['country'] = str(instance.country)

        # Many-to-Many Fields (Genres, Directors, Casts) များကို List of Names အဖြစ်ပြောင်းခြင်း
        response['genres'] = [str(genre) for genre in instance.genres.all()]
        response['directors'] = [str(director) for director in instance.directors.all()]
        response['casts'] = [str(cast) for cast in instance.casts.all()]
        
        return response