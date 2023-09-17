from django.contrib.auth import password_validation
from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = "__all__"


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user

        # Check if the provided old password matches the user's current password
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect old password.")

        return value

    def validate_new_password(self, value):
        # Use Django's built-in password validation to ensure the new password meets security requirements
        password_validation.validate_password(value)

        return value
