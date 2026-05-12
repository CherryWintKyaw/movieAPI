from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Movie, MovieVideo, HeroSection, Country, 
    Genre, Director, Cast, Premiere, Rating
)

# 1. Movie Video Inline - ရုပ်ရှင်တစ်ခုချင်းစီအောက်မှာ Quality အစုံကို လက်နဲ့ဖြည့်ဖို့
class MovieVideoInline(admin.TabularInline):
    model = MovieVideo
    extra = 1
    # အခု ဒီမှာ readonly_fields မပါတော့ပါဘူး၊ ဒါမှ လက်နဲ့ရိုက်လို့ရမှာပါ
    fields = ('quality', 'dood_file_code', 'file_size', 'duration')

# 2. Movie Admin - ရုပ်ရှင်စာရင်းကို စီမံခန့်ခွဲဖို့
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    inlines = [MovieVideoInline]
    
    # Poster ကို Admin List မှာ ပုံလေးနဲ့ မြင်ရအောင်လုပ်ပေးတဲ့ function
    def poster_tag(self, obj):
        if obj.poster:
            return format_html('<img src="{}" style="width: 50px; height:70px; object-fit: cover; border-radius: 4px;" />', obj.poster.url)
        return "-"
    poster_tag.short_description = 'Poster'

    # Admin list မှာ ပြမယ့် Column များ
    list_display = ('poster_tag', 'title', 'release_year', 'rating', 'is_trending', 'view_count', 'created_at')
    
    # ဘေးမှာ Filter လုပ်လို့ရမယ့်အချက်များ
    list_filter = ('is_trending', 'release_year', 'country', 'genres')
    
    # ရှာဖွေလို့ရမယ့် field များ
    search_fields = ('title', 'description')
    
    # Title ရိုက်တာနဲ့ Slug ကို Auto ထွက်စေရန်
    prepopulated_fields = {'slug': ('title',)}
    
    # ManyToMany Field တွေကို Box ၂ ခုနဲ့ လွယ်လွယ်ရွေးဖို့
    filter_vertical = ('genres', 'directors', 'casts')
    
    # အသစ်တင်တဲ့ကား အပေါ်ဆုံးရောက်နေစေဖို့
    ordering = ('-created_at',)

# 3. Hero Section Admin
@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating', 'created_at')

# 4. ကျန်တဲ့ Base Models များကို Register လုပ်ခြင်း
# အကုန်လုံးကို တစ်ပြိုင်တည်း register လုပ်လိုက်တာပါ
admin.site.register([Country, Genre, Director, Cast, Premiere, Rating])