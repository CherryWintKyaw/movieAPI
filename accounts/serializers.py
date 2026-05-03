from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            "id": str(self.user.id),
            "username": self.user.username,
            "email": self.user.email,
            "is_premium": self.user.is_premium
        }
        return data
    
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_premium', 'premium_expiry']    



class UserDetailSerializer(serializers.ModelSerializer):
    # DateTimeField တွေကို format ပြင်လိုက်တာပါ
    # %d/%m/%Y = 03/05/2026
    # %I:%M%p = 01:30PM
    date_joined = serializers.DateTimeField(format="%d/%m/%Y %I:%M%p", read_only=True)
    premium_expiry = serializers.DateTimeField(format="%d/%m/%Y %I:%M%p", read_only=True)
    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email', 
            'role', 
            'is_premium', 
            'premium_expiry', 
            'date_joined', 
            'is_active'
        ]
        # ID, Email နဲ့ join တဲ့ရက်စွဲတွေကို ပြင်ခွင့်မပေးဘဲ Read Only ထားပါမယ်
        read_only_fields = ['id', 'email', 'date_joined']