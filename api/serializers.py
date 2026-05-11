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
             'telegram_channel_id', 'mime_type', 'file_size',
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

from rest_framework import serializers
from .models import Series, Genre, Cast, Director, Country, Rating, Premiere

class SeriesSerializer(serializers.ModelSerializer):
    # Foreign Key တွေကနေ နာမည်တွေကို string အနေနဲ့ တိုက်ရိုက်ဖတ်ပြဖို့ (Read Only)
    country_name = serializers.CharField(source='country.name', read_only=True)
    rating_name = serializers.CharField(source='rating.name', read_only=True)
    release_year_name = serializers.CharField(source='release_year.name', read_only=True)

    # ManyToMany Field တွေကို list အလိုက် နာမည်လေးတွေပဲ ပြချင်ရင်
    genres_list = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='genre',
        source='genres'
    )

    class Meta:
        model = Series
        # field အားလုံးကို ပြချင်ရင် '__all__' သုံးနိုင်ပါတယ်
        # ဒါပေမဲ့ custom field တွေပါချင်ရင် list နဲ့ ရေးတာ ပိုကောင်းပါတယ်
        fields = [
            'id', 'title', 'slug', 'description', 'poster', 
            'status', 'is_trending', 'view_count',
            'country', 'country_name', 
            'rating', 'rating_name',
            'release_year', 'release_year_name',
            'genres', 'genres_list', 
            'directors', 'casts', 
            'created_at', 'updated_at'
        ]
        
        # ID တွေကိုပဲသုံးပြီး create/update လုပ်လို့ရအောင် field တွေကို default ထားပြီး
        # name field တွေကိုပဲ read_only လုပ်ထားတာပါ
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'view_count']