import uuid
from django.db import models
from django.utils.text import slugify

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


class Movie(models.Model):
    # ID ကို UUID ပြောင်းလဲခြင်း
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ရုပ်ရှင်အခြေခံအချက်အလက်များ
    title = models.CharField(max_length=255)
    # Slug field ထည့်သွင်းခြင်း
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    poster = models.ImageField(upload_to='movie_posters/')
    
    # Telegram နှင့် Video အချက်အလက်များ
    video_link = models.URLField(max_length=1000, null=True, blank=True)
    trailer_link = models.URLField(max_length=1000, null=True, blank=True)
    telegram_message_id = models.BigIntegerField(null=True, blank=True)
    telegram_channel_id = models.BigIntegerField(default=-1003967453350)
    mime_type = models.CharField(max_length=100, default='video/mp4')
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # Master Data ချိတ်ဆက်မှုများ
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, related_name='movies')
    rating = models.ForeignKey('Rating', on_delete=models.SET_NULL, null=True, related_name='movies')
    release_year = models.ForeignKey('Premiere', on_delete=models.SET_NULL, null=True, related_name='movies')
    
    genres = models.ManyToManyField('Genre', related_name='movies')
    directors = models.ManyToManyField('Director', related_name='movies')
    casts = models.ManyToManyField('Cast', related_name='movies')
    
    # အပိုဆောင်း အချက်အလက်များ
    duration = models.CharField(max_length=100, null=True, blank=True)
    is_trending = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Slug ကို အလိုလို generate လုပ်ရန်
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"
        ordering = ['-created_at']


# --- Series Model --
class Series(models.Model):
    class SeriesStatus(models.TextChoices):
        ONGOING = 'ONGOING', 'Ongoing'
        COMPLETED = 'COMPLETED', 'Completed'
        UPCOMING = 'UPCOMING', 'Upcoming'
        DROPPED = 'DROPPED', 'Dropped'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    
    # allow_unicode=True ထည့်ရင် မြန်မာစာ title တွေကိုပါ slug ထွက်ပေးနိုင်ပါတယ်
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, allow_unicode=True)
    
    description = models.TextField(null=True, blank=True)
    poster = models.ImageField(upload_to='series_posters/')
    
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, related_name='series_list')
    rating = models.ForeignKey('Rating', on_delete=models.SET_NULL, null=True, related_name='series_list')
    release_year = models.ForeignKey('Premiere', on_delete=models.SET_NULL, null=True, related_name='series_list')
    
    genres = models.ManyToManyField('Genre', related_name='series_list')
    directors = models.ManyToManyField('Director', related_name='series_list')
    casts = models.ManyToManyField('Cast', related_name='series_list')
    
    status = models.CharField(
        max_length=20,
        choices=SeriesStatus.choices,
        default=SeriesStatus.ONGOING,
    )
    
    is_trending = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Title တူရင် slug မထပ်အောင် title + uuid ရဲ့ အရှေ့ပိုင်းကို တွဲသုံးတာ ပိုစိတ်ချရပါတယ်
            base_slug = slugify(self.title, allow_unicode=True)
            self.slug = f"{base_slug}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Series"
        verbose_name_plural = "Series"
        ordering = ['-created_at'] # နောက်ဆုံးတင်တာ အရင်ပြမယ်


# --- Season Model ---
class Season(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='seasons')
    
    season_number = models.IntegerField(default=1) # Season 1, 2, 3...
    title = models.CharField(max_length=255, null=True, blank=True) # ဥပမာ - Season 1: The Beginning
    poster = models.ImageField(upload_to='season_posters/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.series.title} - Season {self.season_number}"

    class Meta:
        verbose_name = "Season"
        verbose_name_plural = "Seasons"
        ordering = ['season_number']


# --- Episode Model ---
class Episode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes')
    
    episode_number = models.IntegerField() # Episode 1, 2, 3...
    title = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    
    # Episode thumbnail
    poster = models.ImageField(upload_to='episode_posters/', null=True, blank=True)
    
    # Telegram Streaming အချက်အလက်များ (Netflix Style အတွက်)
    telegram_channel_id = models.BigIntegerField(default=-1003967453350)
    telegram_message_id = models.BigIntegerField()
    telegram_file_id = models.CharField(max_length=500, null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, default='video/mp4')
    
    video_link = models.URLField(max_length=1000, null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Episode Slug ကို Auto ထုတ်ပေးရန် (ဥပမာ - squid-game-s1-e1)
        if not self.slug:
            self.slug = slugify(f"{self.season.series.title}-s{self.season.season_number}-e{self.episode_number}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.season.series.title} S{self.season.season_number} E{self.episode_number}"

    class Meta:
        verbose_name = "Episode"
        verbose_name_plural = "Episodes"
        ordering = ['episode_number']