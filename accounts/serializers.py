from rest_framework import serializers
from .models import User
from django.contrib.auth.models import Permission, Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

def get_permissions_object_list(permissions_queryset):
    return [
        {"id": p.id, "name": p.name, "codename": p.codename} 
        for p in permissions_queryset
    ]

def get_groups_object_list(groups_queryset):
    return [
        {
            "id": g.id, 
            "name": g.name, 
            "permissions": get_permissions_object_list(g.permissions.all())
        } 
        for g in groups_queryset
    ]
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
    # Groups ကို ID list အနေနဲ့ လက်ခံဖို့ (သို့မဟုတ်) ပို့ပေးဖို့ သတ်မှတ်ခြင်း
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True
    )
    user_permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True
    )
    premium_expiry = serializers.DateTimeField(format="%d/%m/%Y %I:%M%p", read_only=True)

    class Meta:
        model = User
        # fields ထဲမှာ 'groups' ကို ထည့်ပါ
        fields = ['id', 'username', 'email', 'role', 'is_premium', 'premium_expiry', 'groups', 'user_permissions']

    def to_representation(self, instance):
        """Response ပြန်တဲ့အခါ Groups နဲ့ Permissions ကို Object list ပုံစံပြောင်းခြင်း"""
        representation = super().to_representation(instance)
        
        # Groups ကို Object ပုံစံပြောင်းရန်
        representation['groups'] = [
            {"id": g.id, "name": g.name} 
            for g in instance.groups.all()
        ]
        
        # Permissions ကို Object ပုံစံပြောင်းရန်
        representation['user_permissions'] = [
            {"id": p.id, "name": p.name, "codename": p.codename} 
            for p in instance.user_permissions.all()
        ]
        
        return representation
    
    
class UserDetailSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%d/%m/%Y %I:%M%p", read_only=True)
    premium_expiry = serializers.DateTimeField(format="%d/%m/%Y %I:%M%p", read_only=True)
    
    # Groups update လုပ်ရန် ID list လက်ခံမည်
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        required=False
    )
    
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
            'is_active', 'groups', 'user_permissions'
        ]
        read_only_fields = ['id', 'email', 'date_joined']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Group များကို Object ပုံစံဖြင့် ပြန်ပြရန်
        representation['groups'] = [
            {"id": g.id, "name": g.name} 
            for g in instance.groups.all()
        ]
        # Permission များကို Object ပုံစံဖြင့် ပြန်ပြရန်
        representation['user_permissions'] = [
            {"id": p.id, "name": p.name, "codename": p.codename} 
            for p in instance.user_permissions.all()
        ]
        return representation

    def update(self, instance, validated_data):
        # Data များကို pop လုပ်ယူခြင်း
        groups_data = validated_data.pop('groups', None)
        permissions_data = validated_data.pop('user_permissions', None)
        
        # ပုံမှန် field များကို update လုပ်ခြင်း
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Many-to-Many field များကို update လုပ်ခြင်း
        if groups_data is not None:
            instance.groups.set(groups_data)
        
        if permissions_data is not None:
            instance.user_permissions.set(permissions_data)
            
        return instance
    
class GroupSerializer(serializers.ModelSerializer):
    # Group ဆောက်တဲ့အခါ/ပြင်တဲ့အခါ Permission IDs list ပို့ပေးရန်
    permissions = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Permission.objects.all(), 
        required=False
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

    def to_representation(self, instance):
        """Data ပြန်ပြတဲ့အခါ Permission ID သက်သက်မဟုတ်ဘဲ Detail ပါပြရန်"""
        representation = super().to_representation(instance)
        representation['permissions'] = [
            {"id": p.id, "name": p.name, "codename": p.codename} 
            for p in instance.permissions.all()
        ]
        return representation