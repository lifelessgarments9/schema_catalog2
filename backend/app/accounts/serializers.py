from rest_framework import serializers
from app.accounts.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(use_url=True)
    class Meta:
        model = User
        fields = ["id", "username", "email","avatar", "bio" , "is_staff"]
        read_only_fields = ["id"]

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "Passwords don't match"
            })
        return data

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data["user"] = user
        return data