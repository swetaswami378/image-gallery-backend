from rest_framework import serializers
from .models import User, ImageItem
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    total_images = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'total_images', 'date_joined', 'last_login')
        read_only_fields = ('id', 'date_joined', 'last_login')
    
    def get_total_images(self, obj):
        return obj.images.count()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    # password2 = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ("username","email","password")

    # def validate(self, data):
    #     if data["password"] != data["password2"]:
    #         raise serializers.ValidationError({"password":"Passwords don't match."})
    #     return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class ImageItemSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = ImageItem
        fields = ("id","owner","image","image_url","caption","original_filename","uploaded_at","is_captioned")
        read_only_fields = ("caption","is_captioned","uploaded_at","owner","image_url")

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
