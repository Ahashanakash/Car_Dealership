from rest_framework import serializers
from .models import Profile
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = [
            "address",
            "photo",
            "date_of_birth",
            "gender"
        ]
        
        
class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "re_password",
            "is_customer",
            "is_seller"
        )
        def create(self, validated_data):
            first_name = validated_data.pop("first_name", "")
            last_name = validated_data.pop("last_name", "")
            user = super().create(validated_data)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            return user

class UserUpdateSerializer(UserSerializer):

    profile = ProfileSerializer()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "profile"
        )
        read_only_fields = ("email", "username")

    def update(self, instance, validated_data):

        profile_data = validated_data.pop("profile", None)

        # update user
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # update profile
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance
        