import uuid
import asyncio
import threading
from django.db import models
from django.utils.text import slugify
from django.conf import settings
from telethon import TelegramClient
from telethon.sessions import StringSession
from asgiref.sync import sync_to_async
from django.dispatch import receiver
from django.db.models.signals import post_save

class HeroSection(models.Model):
    # ID ကို UUID ပြောင်းလဲခြင်း
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    title = models.CharField(max_length=255, null=True, blank=True, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    button_text = models.CharField(max_length=50, null=True, blank=True)
    link = models.URLField(max_length=500, null=True, blank=True)
    
    image = models.ImageField(upload_to='hero_images/')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title if self.title else f"Hero Content {self.id}"

    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Sections"



class Country(models.Model):
    # ID ကို UUID ပြောင်းလဲခြင်း
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # နိုင်ငံအမည် (ဥပမာ - Myanmar, Korea, Thailand)
    country = models.CharField(max_length=100, unique=True)
    
    # အချိန်မှတ်တမ်းများ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.country

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ['country'] # နိုင်ငံအမည်အတိုင်း အစဉ်လိုက်ပြပေးဖို့



class Genre(models.Model):
    # ID ကို UUID ပြောင်းလဲခြင်း
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # အမျိုးအစားအမည် (ဥပမာ - Action, Comedy, Drama, Horror)
    genre = models.CharField(max_length=100, unique=True)
    
    # အချိန်မှတ်တမ်းများ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.genre

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        ordering = ['genre'] # အမျိုးအစားအမည်အတိုင်း အက္ခရာစဉ်စီရန်

class Director(models.Model):
    # ID ကို UUID ပြောင်းလဲခြင်း
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ဒါရိုက်တာအမည်
    director = models.CharField(max_length=255, unique=True)
    
    # ဒါရိုက်တာ၏ ဓာတ်ပုံ (director_images ဆိုတဲ့ folder ထဲကို သိမ်းပါမယ်)
    # null=True, blank=True ထည့်ထားတာက ပုံမရှိလည်း save လို့ရအောင်ပါ
    image = models.ImageField(upload_to='director_images/', null=True, blank=True)
    
    # အချိန်မှတ်တမ်းများ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.director

    class Meta:
        verbose_name = "Director"
        verbose_name_plural = "Directors"
        ordering = ['director']


class Cast(models.Model):
    # ID ကို UUID ပြောင်းလဲခြင်း
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # သရုပ်ဆောင်အမည်ကို unique=True ထည့်လိုက်ပါ
    # ဒါဆိုရင် နာမည်တူ နောက်တစ်ခု ထပ်ဆောက်လို့မရတော့ပါဘူး
    cast = models.CharField(max_length=255, unique=True)
    
    # သရုပ်ဆောင်၏ ဓာတ်ပုံ
    image = models.ImageField(upload_to='cast_images/', null=True, blank=True)
    
    # အချိန်မှတ်တမ်းများ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cast

    class Meta:
        verbose_name = "Cast"
        verbose_name_plural = "Casts"
        ordering = ['cast']

class Premiere(models.Model):
    # ID ကို UUID ပြောင်းလဲခြင်း
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ထွက်ရှိသည့် ခုနှစ် (ဥပမာ - 2024, 2025)
    # IntegerField သုံးတာက ရှာရဖွေရ ပိုလွယ်ကူစေပါတယ်
    year = models.IntegerField(unique=True)
    
    # အချိန်မှတ်တမ်းများ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.year)

    class Meta:
        verbose_name = "Premiere Year"
        verbose_name_plural = "Premiere Years"
        ordering = ['-year'] # ခုနှစ်အသစ်တွေကို အပေါ်ဆုံးကပြရန်

class Rating(models.Model):
    # ID ကို UUID ပြောင်းလဲခြင်း
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Rating တန်ဖိုး (ဥပမာ - 8.5, 9.0)
    # max_digits=3, decimal_places=1 ဆိုလျှင် 10.0 အထိ သိမ်းလို့ရပါတယ်
    rating = models.DecimalField(max_digits=3, decimal_places=1,unique=True)
    
    # အချိန်မှတ်တမ်းများ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.rating}"

    class Meta:
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"
        ordering = ['-rating'] # Rating အမြင့်ဆုံးကားတွေကို အပေါ်ဆုံးကပြရန်



import uuid
import requests
import threading
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# --- Movie Model ---
class Movie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    poster = models.ImageField(upload_to='movie_posters/')
    
    # Relationships (မင်းအရင်ရေးထားတဲ့ models တွေနဲ့ ချိတ်မယ်)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, related_name='movies')
    rating = models.ForeignKey('Rating', on_delete=models.SET_NULL, null=True, related_name='movies')
    release_year = models.ForeignKey('Premiere', on_delete=models.SET_NULL, null=True, related_name='movies')
    genres = models.ManyToManyField('Genre', related_name='movies')
    directors = models.ManyToManyField('Director', related_name='movies', blank=True)
    casts = models.ManyToManyField('Cast', related_name='movies', blank=True)
    
    is_trending = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# --- Movie Video Model (DoodStream Focused) ---
class MovieVideo(models.Model):
    QUALITY_CHOICES = [
        ('360p','360p'),
        ('480p','480p'),
        ('720p','720p'),
        ('1080p','1080p'),
        ('4K','4K')
    ]
    
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='videos')
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES, null=True, blank=True)
    
    # DoodStream API အတွက် အရေးကြီးဆုံးကွက်
    dood_file_code = models.CharField(
        max_length=100, 
        help_text="DoodStream File Code (ဥပမာ- 6def7f95aa50)"
    )
    
    # Metadata (API ကနေ Auto ဖြည့်ပေးမယ့်အပိုင်း)
    file_size = models.CharField(max_length=100, null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    thumbnail_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.movie.title} - {self.quality}"

    @property
    def embed_url(self):
        return f"https://doodstream.com/e/{self.dood_file_code}"

# --- DoodStream Metadata Fetcher (Background Thread) ---
def fetch_dood_metadata(video_id):
    try:
        video = MovieVideo.objects.get(id=video_id)
        api_key = settings.DOODSTREAM_API_KEY
        url = f"https://doodapi.com/api/file/info?key={api_key}&file_code={video.dood_file_code}"
        
        # verify=False ထည့်လိုက်တာက SSL error ကို ကျော်သွားစေပါတယ်
        response = requests.get(url, verify=False).json()
        
        if response['status'] == 200 and response['result']:
            data = response['result'][0]
            
            # Size ကို MB ပြောင်းမယ်
            size_bytes = int(data.get('size', 0))
            size_mb = round(size_bytes / (1024 * 1024), 2)
            
            # Duration ကို format လုပ်မယ်
            length_sec = int(data.get('length', 0))
            h = length_sec // 3600
            m = (length_sec % 3600) // 60
            duration_str = f"{h}h {m}m" if h > 0 else f"{m}m"
            
            # DB မှာ အမှန်တကယ် သွားသိမ်းမယ်
            video.file_size = f"{size_mb} MB"
            video.duration = duration_str
            video.thumbnail_url = data.get('single_img')
            video.save(update_fields=['file_size', 'duration', 'thumbnail_url'])
            
            print(f"✅ Metadata Updated for {video.dood_file_code}")
            
    except Exception as e:
        print(f"❌ DoodStream API Error: {str(e)}")
        
# --- Signal to trigger API Call ---
@receiver(post_save, sender=MovieVideo)
def trigger_metadata_fetch(sender, instance, created, **kwargs):
    # အသစ်ဆောက်ချိန် ဒါမှမဟုတ် metadata မရှိသေးရင် API ခေါ်မယ်
    if created or not instance.file_size:
        thread = threading.Thread(target=fetch_dood_metadata, args=(instance.id,))
        thread.daemon = True
        thread.start()