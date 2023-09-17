from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.db import transaction
from django.contrib.auth import authenticate

# PASSWORD CHANGE VIEW
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from . import models, serializers


class UserLoginView(APIView):
    """The UserLoginview returns an authorization token when a user logs in"""

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            # Create or retrieve an existing token for the user
            token, created = Token.objects.get_or_create(user=user)
            user.last_login = timezone.now()
            user.save()
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    """Deletes the user authorization token"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = Token.objects.get(user=user)

        token.delete()
        return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)


class UserRegistrationView(CreateAPIView):
    """Gets new user details, sets the password and return user data"""

    serializer_class = serializers.UserSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():  # Rolls back data from database if error occurs
                data = serializer.save()
                data.set_password(data.password)
                data.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_mail(self, request, email):
        pass


class UserProfileView(RetrieveUpdateDestroyAPIView):
    """Uses ID to find user and sets user to inactive instead of deleting data"""

    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        with transaction.atomic():
            instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if email:
            user = models.User.objects.filter(email=email).first()
            if user:
                # Generate a password reset token and send it to the user via email
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = f"{settings.FRONTEND_RESET_URL}/{uidb64}/{token}/"
                email_subject = "Password Reset"
                email_message = render_to_string("password_reset_email.html", {"reset_url": reset_url})
                send_mail(email_subject, email_message, settings.EMAIL_FROM, [email])

        # Return a response indicating that a password reset email has been sent
        return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)


class PasswordChangeView(UpdateAPIView):
    serializer_class = serializers.PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.request.user.set_password(serializer.validated_data["new_password"])
            self.request.user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
