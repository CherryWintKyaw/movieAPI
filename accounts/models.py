import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        OWNER = "owner", "Shop Owner"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    is_premium = models.BooleanField(default=False)
    premium_expiry = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def check_premium_status(self):
        if self.is_premium and self.premium_expiry:
            if timezone.now() > self.premium_expiry:
                self.is_premium = False
                self.save()
        return self.is_premium

class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [(1, '1 Month'), (6, '6 Months'), (12, '1 Year')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan_type = models.IntegerField(choices=PLAN_CHOICES)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.user.is_premium = True
            start_date = self.user.premium_expiry if self.user.premium_expiry and self.user.premium_expiry > timezone.now() else timezone.now()
            self.user.premium_expiry = start_date + timedelta(days=30 * self.plan_type)
            self.user.save()
        super().save(*args, **kwargs)