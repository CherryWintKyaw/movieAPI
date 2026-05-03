from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SubscriptionPlan

class CustomUserAdmin(UserAdmin):
    # Admin Panel ရဲ့ List view မှာ ပြမယ့် Column များ
    list_display = ('email', 'username', 'role', 'is_premium', 'premium_expiry', 'is_staff')
    
    # ဘေးဘက်မှာ Filter ပေးမယ့် Field များ
    list_filter = ('role', 'is_premium', 'is_staff', 'is_active')
    
    # ရှာဖွေရလွယ်ကူအောင် လုပ်ထားတဲ့ Field များ
    search_fields = ('email', 'username')
    ordering = ('email',)

    # User Detail (Edit) page မှာ အချက်အလက်တွေကို အုပ်စုခွဲပြခြင်း
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'is_premium', 'premium_expiry')}),
    )
    
    # User အသစ်ဆောက်တဲ့ page အတွက် (Optional)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'is_premium', 'premium_expiry')}),
    )

# Subscription History ကိုလည်း Admin ကနေ ကြည့်လို့ရအောင် ထည့်ထားပေးပါတယ်
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_type', 'purchased_at')
    list_filter = ('plan_type', 'purchased_at')
    search_fields = ('user__email', 'user__username')

# Model များကို Register လုပ်ခြင်း
admin.site.register(User, CustomUserAdmin)
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)