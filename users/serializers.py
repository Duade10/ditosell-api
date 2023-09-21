from django.contrib.auth import password_validation
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from db_connection import db
from . import models


def validate_email(email):
    users = db["users"]
    existing_user = users.find_one({"email": email})
    if existing_user:
        raise serializers.ValidationError({"Error": "Email Already In Use"})
    return email


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    user_type = serializers.ChoiceField(choices=models.USER_TYPES, required=False)
    login_type = serializers.ChoiceField(choices=models.LOGIN_TYPES, required=False)
    is_active = serializers.BooleanField()
    password = serializers.CharField(write_only=True, required=True)
    last_login = serializers.DateTimeField(read_only=True, default=timezone.now())

    def create(self, validated_data):
        """
        Create and return a new User instance, given the validated data.
        """

        validate_email(validated_data["email"])
        password = validated_data["password"]
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        # Create the user
        user_dict = dict(validated_data)
        user = models.User(user_dict)
        return user.add_user()


class PasswordChangeSerializer(serializers.Serializer):
    verification_token = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, obj):
        is_same = obj["new_password"] == obj["confirm_password"]
        if is_same:
            return obj
        else:
            raise ValidationError({"Error": "Error Matching Password"})

    def validate_new_password(self, value):
        # Use Django's built-in password validation to ensure the new password meets security requirements
        password_validation.validate_password(value)
        return value


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["name"] = user.email.split("@")[0]
        return token
