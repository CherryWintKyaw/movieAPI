from rest_framework import serializers
from .models import User
from django.contrib.auth.models import Permission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# --- 1. Register Serializer ---
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)

# --- 2. Login Serializer ---
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Login ဝင်ချိန်တွင် Object ပုံစံလိုချင်ပါက ဤနေရာတွင် ပြင်နိုင်သည်
        data['user'] = {
            "id": str(self.user.id),
            "username": self.user.username,
            "email": self.user.email,
            "role": self.user.role,
            "is_premium": self.user.is_premium,
            "permissions": [
                {"id": p.id, "name": p.name, "codename": p.codename} 
                for p in self.user.user_permissions.all()
            ]
        }
        return data

# --- 3. User List Serializer ---
class UserListSerializer(serializers.ModelSerializer):
    user_permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True
    )
    premium_expiry = serializers.DateTimeField(format="%d/%m/%Y %I:%M%p", read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_premium', 'premium_expiry', 'user_permissions']

    def to_representation(self, instance):
        """Response ပြန်ခါနီးမှ ID list ကို Object list အဖြစ် ပြောင်းလဲပေးခြင်း"""
        representation = super().to_representation(instance)
        representation['user_permissions'] = [
            {"id": p.id, "name": p.name, "codename": p.codename} 
            for p in instance.user_permissions.all()
        ]
        return representation

# --- 4. User Detail & Update Serializer ---
class UserDetailSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%d/%m/%Y %I:%M%p", read_only=True)
    premium_expiry = serializers.DateTimeField(format="%d/%m/%Y %I:%M%p", read_only=True)
    
    # Update အတွက် ID list ကို လက်ခံရန်
    user_permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 
            'is_premium', 'premium_expiry', 'date_joined', 
            'is_active', 'user_permissions'
        ]
        read_only_fields = ['id', 'email', 'date_joined']

    def to_representation(self, instance):
        """GET request သို့မဟုတ် Update ပြီးနောက် ပြန်ပြမည့် JSON ကို Object ပုံစံပြောင်းခြင်း"""
        representation = super().to_representation(instance)
        representation['user_permissions'] = [
            {"id": p.id, "name": p.name, "codename": p.codename} 
            for p in instance.user_permissions.all()
        ]
        return representation

    def update(self, instance, validated_data):
        # user_permissions data ကို ယူပြီး handle လုပ်ခြင်း
        permissions_data = validated_data.pop('user_permissions', None)
        
        # အခြား field များကို ပုံမှန်အတိုင်း update လုပ်ခြင်း
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Permission များကို Many-to-Many relationship အနေဖြင့် သိမ်းဆည်းခြင်း
        if permissions_data is not None:
            instance.user_permissions.set(permissions_data)
            
        return instance