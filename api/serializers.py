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

class MovieSerializer(serializers.ModelSerializer):
    # Slug ကို auto generate လုပ်ထားလို့ read_only ထည့်ထားသင့်ပါတယ်
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Movie
        fields = '__all__'
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at']

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