import uuid
from django.db import models

class HeroSection(models.Model):
    # ID ကို UUID ပြောင်းလဲခြင်း
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    title = models.CharField(max_length=255, null=True, blank=True)
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