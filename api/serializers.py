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

# Main Movie Serializer
class MovieSerializer(serializers.ModelSerializer):
    # GET request လုပ်တဲ့အခါ ID အစား နာမည်/အချက်အလက် အပြည့်အစုံ မြင်ရစေရန် (Read Only)
    country_detail = CountrySerializer(source='country', read_only=True)
    rating_detail = RatingSerializer(source='rating', read_only=True)
    release_year_detail = PremiereSerializer(source='release_year', read_only=True)
    genres_detail = GenreSerializer(source='genres', many=True, read_only=True)
    directors_detail = DirectorSerializer(source='directors', many=True, read_only=True)
    casts_detail = CastSerializer(source='casts', many=True, read_only=True)

    # Video Stream Link ကို အလိုအလျောက် generate လုပ်ပေးရန် (Optional)
    stream_url = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'slug', 'description', 'poster',
            'video_link', 'trailer_link', 'telegram_message_id', 
            'telegram_file_id', 'telegram_channel_id', 'mime_type', 'file_size',
            'country', 'country_detail',
            'rating', 'rating_detail',
            'release_year', 'release_year_detail',
            'genres', 'genres_detail',
            'directors', 'directors_detail',
            'casts', 'casts_detail',
            'duration', 'is_trending', 'view_count', 'stream_url',
            'created_at', 'updated_at'
        ]
        # POST/PUT လုပ်တဲ့အခါ ID ပဲ ပို့လို့ရအောင် extra_kwargs သုံးနိုင်ပါတယ်
        extra_kwargs = {
            'country': {'write_only': True},
            'rating': {'write_only': True},
            'release_year': {'write_only': True},
            'genres': {'write_only': True},
            'directors': {'write_only': True},
            'casts': {'write_only': True},
            'slug': {'read_only': True}, # Save method ကနေ generate လုပ်မှာမို့လို့ပါ
        }

    def get_stream_url(self, obj):
        # Telegram Stream API ရဲ့ URL ကို တစ်ခါတည်း ဆောက်ပေးလိုက်တာပါ
        if obj.telegram_channel_id and obj.telegram_message_id:
            # Domain နေရာမှာ သင့်ရဲ့ server domain ကို ပြောင်းပေးပါ
            return f"/api/stream/{obj.telegram_channel_id}/{obj.telegram_message_id}/"
        return None

class EpisodeSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)
    class Meta:
        model = Episode
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class SeasonSerializer(serializers.ModelSerializer):
    # Season အောက်မှာရှိတဲ့ Episode တွေကို list လိုက် မြင်ချင်ရင်
    episodes = EpisodeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Season
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class SeriesSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)
    # Series အောက်မှာရှိတဲ့ Season တွေကို list လိုက် မြင်ချင်ရင်
    seasons = SeasonSerializer(many=True, read_only=True)

    class Meta:
        model = Series
        fields = '__all__'
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at']