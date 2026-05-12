from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Movie, MovieVideo, HeroSection, Country, 
    Genre, Director, Cast, Premiere, Rating
)

# 1. Video Inline - Movie တစ်ခုအောက်မှာ Quality အစုံထည့်ဖို့
class MovieVideoInline(admin.TabularInline):
    model = MovieVideo
    extra = 1
    # Metadata တွေကို API ကနေ auto ဖြည့်မှာမို့လို့ readonly ထားပါတယ်
    readonly_fields = ('file_size', 'duration', 'thumbnail_url')
    fields = ('quality', 'dood_file_code', 'file_size', 'duration', 'thumbnail_url')

# 2. Movie Admin
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    inlines = [MovieVideoInline]
    
    # Poster ကို Thumbnail ပြရန်
    def poster_tag(self, obj):
        if obj.poster:
            return format_html('<img src="{}" style="width: 50px; height:70px; object-fit: cover; border-radius: 4px;" />', obj.poster.url)
        return "-"
    poster_tag.short_description = 'Poster'

    # Admin List မှာ ပြမယ့် Columns (မင်း Model ထဲက နာမည်တွေအတိုင်း ပြင်ထားတယ်)
    list_display = ('poster_tag', 'title', 'release_year', 'rating', 'is_trending', 'view_count')
    
    # Filter လုပ်လို့ရမယ့်အချက်များ
    list_filter = ('is_trending', 'release_year', 'country', 'genres')
    
    # ရှာဖွေလို့ရမယ့် field များ
    search_fields = ('title', 'description')
    
    # Title ရိုက်တာနဲ့ Slug ကို Auto ထွက်စေရန်
    prepopulated_fields = {'slug': ('title',)}
    
    # ManyToMany Field တွေကို Box ၂ ခုနဲ့ လွယ်လွယ်ရွေးဖို့
    filter_vertical = ('genres', 'directors', 'casts')

# 3. ကျန်တဲ့ Base Models များကို Register လုပ်ခြင်း
@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating', 'created_at')

admin.site.register(Country)
admin.site.register(Genre)
admin.site.register(Director)
admin.site.register(Cast)
admin.site.register(Premiere)
admin.site.register(Rating)