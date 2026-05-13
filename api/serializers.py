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
    
    # Movie ID ကို လက်ခံဖို့ write_only field ထည့်ပါ
    movie = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all(), write_only=True)

    class Meta:
        model = MovieVideo
        fields = ['id', 'movie', 'quality', 'play_url', 'dood_file_code', 'file_size', 'duration']

class MovieSerializer(serializers.ModelSerializer):
    # read_only=True ပြောင်းလိုက်ပါ (ဒါဆိုရင် create လုပ်တဲ့အခါ video ထည့်စရာမလိုတော့ဘူး)
    videos = MovieVideoSerializer(many=True, read_only=True) 
    
    # ... ကျန်တဲ့ directors, casts စတာတွေကတော့ အရင်အတိုင်းပဲ ...

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'slug', 'description', 'poster', 
            'country', 'rating', 'release_year', 'genres', 
            'directors', 'casts', 'is_trending', 'view_count', 
            'videos', 'created_at'
        ]
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
    
    #season
class SeasonSerializer(serializers.ModelSerializer):
    # POST/PUT လုပ်တဲ့အခါ Series ID ကို လက်ခံဖို့
    series = serializers.PrimaryKeyRelatedField(queryset=Series.objects.all())

    class Meta:
        model = Season
        fields = [
            'id', 
            'series', 
            'season_number', 
            'description', 
            'created_at'
        ]

    def to_representation(self, instance):
        """
        Data ပြန်ထုတ်ပြတဲ့အခါ Series ID အစား Series နာမည်ကို ပြောင်းလဲပြသခြင်း
        """
        response = super().to_representation(instance)
        
        # series object ရှိမရှိ စစ်ဆေးပြီး String အဖြစ်ပြောင်းမယ်
        if instance.series:
            response['series_name'] = instance.series.title
            # တကယ်လို့ response['series'] နေရာမှာပဲ နာမည်ပြချင်ရင် အောက်ကအတိုင်း ရေးနိုင်ပါတယ်
            response['series'] = instance.series.title
            
        return response

    def validate(self, data):
        """
        Series တစ်ခုထဲမှာ Season Number ထပ်မနေအောင် စစ်ဆေးခြင်း (Custom Validation)
        """
        series = data.get('series')
        season_number = data.get('season_number')

        # အသစ်ဆောက်တဲ့အခါ (သို့) ပြင်ဆင်တဲ့အခါ Season Number တူနေလား စစ်မယ်
        if Season.objects.filter(series=series, season_number=season_number).exists():
            # Update လုပ်နေတာဆိုရင် ကိုယ့် ID ကိုယ် ပြန်မစစ်မိအောင် လုပ်ဖို့လိုနိုင်ပါတယ်
            if not self.instance or self.instance.season_number != season_number:
                raise serializers.ValidationError(
                    f"Season {season_number} for this series already exists."
                )
        
        return data
    
#episode
class EpisodeSerializer(serializers.ModelSerializer):
    # POST/PUT လုပ်တဲ့အခါ ဘယ် Season အောက်ကလဲဆိုတာ သိဖို့ Season ID လက်ခံမယ်
    season = serializers.PrimaryKeyRelatedField(queryset=Season.objects.all())

    class Meta:
        model = Episode
        fields = [
            'id', 
            'season', 
            'episode_number', 
            'title', 
            'video_file', 
            'view_count', 
            'created_at'
        ]

    def to_representation(self, instance):
        """
        Data ပြန်ထုတ်ပြတဲ့အခါ Season ID အစား Season Number နဲ့ Series Title ကိုပါ ပြသခြင်း
        """
        response = super().to_representation(instance)
        
        if instance.season:
            # Season အချက်အလက်
            response['season_number'] = instance.season.season_number
            # Series အချက်အလက် (Relationship ကဆင့်တက်ကြည့်တာပါ)
            response['series_title'] = instance.season.series.title
            
            # response['season'] နေရာမှာပဲ စာသားပြချင်ရင်
            response['season'] = f"Season {instance.season.season_number}"
            
        return response

    def validate(self, data):
        """
        Season တစ်ခုတည်းမှာ Episode Number ထပ်မနေအောင် စစ်ဆေးခြင်း
        """
        season = data.get('season')
        episode_number = data.get('episode_number')

        # အသစ်ဆောက်ရင် (သို့) နံပါတ်ပြောင်းရင် စစ်မယ်
        if Episode.objects.filter(season=season, episode_number=episode_number).exists():
            if not self.instance or self.instance.episode_number != episode_number:
                raise serializers.ValidationError(
                    f"Episode {episode_number} already exists in this season."
                )
        
        return data
    
# Episode Serializer (အခြေခံ အချက်အလက်ပဲ ပြမယ်)
class EpisodeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ['id', 'episode_number', 'title', 'video_file', 'view_count']

# Season Serializer (Episodes တွေကို တွဲထည့်မယ်)
class SeasonDetailSerializer(serializers.ModelSerializer):
    episodes = EpisodeDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = ['id', 'season_number', 'description', 'episodes']

# Main Series Serializer (Seasons တွေကို တွဲထည့်မယ်)
class SeriesDetailSerializer(serializers.ModelSerializer):
    seasons = SeasonDetailSerializer(many=True, read_only=True) # Nested Relation
    
    # ကျန်တဲ့ fields တွေကတော့ အရင်အတိုင်းပဲ
    class Meta:
        model = Series
        fields = [
            'id', 'title', 'slug', 'description', 'poster', 
            'country', 'rating', 'release_year', 'genres', 
            'directors', 'casts', 'is_trending', 'view_count', 
            'seasons', 'created_at'
        ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        # အရင်ရေးထားတဲ့ ID to Name ပြောင်းတဲ့ logic တွေ ဒီမှာ ဆက်သုံးလို့ရပါတယ်
        if instance.country: response['country'] = str(instance.country)
        if instance.rating: response['rating'] = str(instance.rating)
        response['genres'] = [str(g) for g in instance.genres.all()]
        return response