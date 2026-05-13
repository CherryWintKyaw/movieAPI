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




# --- 3. Movie Model ---
class Movie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    poster = models.ImageField(upload_to='movie_posters/')
    
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='movies')
    rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, null=True, related_name='movies')
    release_year = models.ForeignKey(Premiere, on_delete=models.SET_NULL, null=True, related_name='movies')
    genres = models.ManyToManyField(Genre, related_name='movies')
    directors = models.ManyToManyField(Director, related_name='movies', blank=True)
    casts = models.ManyToManyField(Cast, related_name='movies', blank=True)
    
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

# --- 4. Movie Video Model ---
class MovieVideo(models.Model):
    QUALITY_CHOICES = [
        ('360p','360p'), ('480p','480p'), ('720p','720p'), ('1080p','1080p'), ('4K','4K')
    ]
    
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='videos')
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES, null=True, blank=True)
    dood_file_code = models.CharField(max_length=100, help_text="DoodStream File Code (ဥပမာ - y1kr94f8in6y)")
    
    # လက်နဲ့ ကိုယ်တိုင်ရိုက်ထည့်မည့် Field များ
    file_size = models.CharField(max_length=100, null=True, blank=True, help_text="ဥပမာ - 1.2 GB")
    duration = models.CharField(max_length=100, null=True, blank=True, help_text="ဥပမာ - 1h 52m")

    def __str__(self):
        return f"{self.movie.title} - {self.quality}"

    @property
    def embed_url(self):
        return f"https://doodstream.com/e/{self.dood_file_code}"
    
#series

class Series(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255, db_index=True, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    poster = models.ImageField(upload_to='series_posters/')
    
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='series')
    rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, null=True, related_name='series')
    release_year = models.ForeignKey(Premiere, on_delete=models.SET_NULL, null=True, related_name='series')
    genres = models.ManyToManyField(Genre, related_name='series')
    directors = models.ManyToManyField(Director, related_name='series', blank=True)
    casts = models.ManyToManyField(Cast, related_name='series', blank=True)
    
    is_trending = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Series"

    def save(self, *args, **kwargs):
        if not self.slug:
            # အခြေခံ slug ဖန်တီးမယ်
            base_slug = slugify(self.title)
            # တကယ်လို့ slug က ရှိနေပြီးသားဆိုရင် random string လေး ကပ်ပေးမယ်
            if Series.objects.filter(slug=base_slug).exists():
                self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
            else:
                self.slug = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Season(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='seasons')
    season_number = models.PositiveIntegerField()
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['season_number']

    def __str__(self):
        return f"{self.series.title} - Season {self.season_number}"

class Episode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    
    # Movie လိုပဲ DoodStream အတွက် ပြောင်းလဲခြင်း
    dood_file_code = models.CharField(max_length=100, null=True, blank=True)
    file_size = models.CharField(max_length=100, null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['episode_number']

    @property
    def embed_url(self):
        if self.dood_file_code:
            return f"https://doodstream.com/e/{self.dood_file_code}"
        return None

    def __str__(self):
        return f"{self.season.series.title} S{self.season.season_number} E{self.episode_number}"