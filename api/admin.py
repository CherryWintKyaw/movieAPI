from django.contrib import admin
from .models import (
    HeroSection, Country, Genre, Director, 
    Cast, Premiere, Rating, Movie, Series, Season, Episode
)

# --- Common Config ---
admin.site.site_header = "Streaming Platform Admin"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to Video Streaming Management"

# --- Master Data Admins ---
@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating', 'button_text', 'created_at')
    search_fields = ('title',)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('country', 'created_at')
    search_fields = ('country',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('genre', 'created_at')
    search_fields = ('genre',)

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('director', 'created_at')
    search_fields = ('director',)

@admin.register(Cast)
class CastAdmin(admin.ModelAdmin):
    list_display = ('cast', 'created_at')
    search_fields = ('cast',)

@admin.register(Premiere)
class PremiereAdmin(admin.ModelAdmin):
    list_display = ('year', 'created_at')
    ordering = ('-year',)
    search_fields = ('year',) # ဒီ line အသစ်ထည့်လိုက်ပါ (Autocomplete အတွက် လိုအပ်သည်)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('rating', 'created_at')
    ordering = ('-rating',)
    search_fields = ('rating',) # ဒီ line အသစ်ထည့်လိုက်ပါ (Autocomplete အတွက် လိုအပ်သည်)

# --- Movie Admin ---
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'country', 'rating', 'is_trending', 'view_count')
    list_filter = ('is_trending', 'country', 'release_year', 'genres')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)} # Title ရိုက်ရင် slug auto ထွက်လာအောင်
    autocomplete_fields = ['country', 'rating', 'release_year', 'genres', 'directors', 'casts']
    readonly_fields = ('view_count',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'poster', 'duration')
        }),
        ('Streaming Metadata (Telegram)', {
            'fields': ('telegram_channel_id', 'telegram_message_id',  'mime_type', 'file_size', 'video_link', 'trailer_link')
        }),
        ('Categorization', {
            'fields': ('country', 'rating', 'release_year', 'genres', 'directors', 'casts')
        }),
        ('Status & Analytics', {
            'fields': ('is_trending', 'view_count')
        }),
    )

# --- Series, Season, Episode Inlines ---
class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 1
    fields = ('episode_number', 'title', 'telegram_message_id', 'duration')
    show_change_link = True # Episode တစ်ခုချင်းစီကို သွားပြင်ချင်ရင် လွယ်အောင်

class SeasonInline(admin.StackedInline):
    model = Season
    extra = 1
    show_change_link = True

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'release_year', 'country', 'is_trending', 'view_count')
    list_filter = ('status', 'is_trending', 'country', 'genres')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['country', 'rating', 'release_year', 'genres', 'directors', 'casts']
    inlines = [SeasonInline] # Series အောက်မှာတင် Season တန်းထည့်လို့ရအောင်
    readonly_fields = ('view_count',)

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'series', 'season_number')
    list_filter = ('series',)
    inlines = [EpisodeInline] # Season အောက်မှာတင် Episode တန်းထည့်လို့ရအောင်

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_series', 'get_season', 'episode_number', 'created_at')
    list_filter = ('season__series', 'season')
    search_fields = ('title', 'season__series__title')
    readonly_fields = ('slug',)

    # Admin မှာ Series နာမည်နဲ့ Season နာမည် ပြပေးဖို့ helper functions
    def get_series(self, obj):
        return obj.season.series.title
    get_series.short_description = 'Series'

    def get_season(self, obj):
        return f"Season {obj.season.season_number}"
    get_season.short_description = 'Season'