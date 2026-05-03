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
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)

class User(AbstractUser):
    # UUID ကို Primary Key အဖြစ် အသုံးပြုခြင်း
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        OWNER = "owner", "Shop Owner"

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.CUSTOMER
    )
    is_premium = models.BooleanField(default=False)
    premium_expiry = models.DateTimeField(blank=True, null=True)

    # Login ဝင်ရန် Email ကို အသုံးပြုမည်
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        # Custom Permissions များ သတ်မှတ်ခြင်း
        permissions = [
            ("can_manage_shops", "Can create and manage shops"),
            ("can_access_premium_content", "Can access premium video content"),
        ]

    def __str__(self):
        return self.email

    def check_premium_status(self):
        """Premium သက်တမ်းကုန်မကုန် စစ်ဆေးပြီး Update လုပ်ပေးသည့် Method"""
        if self.is_premium and self.premium_expiry:
            if timezone.now() > self.premium_expiry:
                self.is_premium = False
                self.save()
        return self.is_premium

    def has_role_perm(self, perm_name):
        """Role နှင့် Premium ပေါ်မူတည်၍ Permission ရှိမရှိ စစ်ဆေးသည့် Helper"""
        if self.is_superuser:
            return True
        if self.role == self.Role.OWNER and perm_name == "can_manage_shops":
            return True
        if self.is_premium and perm_name == "can_access_premium_content":
            return True
        return False

class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        (1, '1 Month'), 
        (6, '6 Months'), 
        (12, '1 Year')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan_type = models.IntegerField(choices=PLAN_CHOICES)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # အသစ်ဝယ်ယူသည့်အခါ (Object ဆောက်သည့်အခါ) သာ အလုပ်လုပ်မည်
        if not self.pk:
            self.user.is_premium = True
            
            # လက်ရှိ သက်တမ်းရှိနေသေးရင် အဲ့ဒီအပေါ်မှာ ထပ်ပေါင်းမယ်၊ မရှိရင် အခုကစတွက်မယ်
            start_date = (
                self.user.premium_expiry 
                if self.user.premium_expiry and self.user.premium_expiry > timezone.now() 
                else timezone.now()
            )
            
            # Plan_type (လ) အလိုက် ရက်ပေါင်း ၃၀ စီ မြှောက်ပြီး ပေါင်းမည်
            self.user.premium_expiry = start_date + timedelta(days=30 * self.plan_type)
            self.user.save()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.get_plan_type_display()}"