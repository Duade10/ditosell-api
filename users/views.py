import json
import uuid

import bcrypt
import jwt
import requests
from django.conf import settings

# PASSWORD CHANGE VIEW
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils import timezone
from google_auth_oauthlib.flow import Flow
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse

from db_connection import db

from . import models, serializers
from .authentications import CustomTokenAuthentication
from .permissions import CustomPermission


def generate_token(user_id) -> dict:
    tokens = db["token"]
    payload = {"uuid": str(uuid.uuid4())}
    key = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    old_token = tokens.find_one({"user_id": user_id})
    if old_token:
        tokens.update_one({"_id": old_token["_id"]}, {"$set": {"is_valid": False}})
    token = {"key": key, "uuid": payload["uuid"], "is_valid": True, "user_id": user_id}
    tokens.insert_one(token)
    return token


class UserLoginView(APIView):
    """The UserLoginView returns an authorization token when a user logs in"""

    authentication_classes = [models.MongoDBAuthentication]
    permission_classes = []

    def post(self, request):
        users = db["users"]

        user, _ = self.authentication_classes[0]().authenticate(request)

        if user:
            token = generate_token(user["id"])
            user["last_login"] = timezone.now()
            users.update_one({"id": user["id"]}, {"$set": {"last_login": user["last_login"]}})

            return Response({"token": token["key"], "message": "Login Successful"}, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    """Invalidates the user authorization token"""

    authentication_classes = [models.MongoDBAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        if user:
            token_blacklist = db["token_blacklist"]
            token_blacklist.insert_one({"token": request.auth})

            return Response({"detail": "Successfully Logged Out"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid User"}, status=status.HTTP_401_UNAUTHORIZED)


class UserRegistrationView(CreateAPIView):
    """Gets new user details, sets the password and return user data"""

    serializer_class = serializers.UserSerializer

    def post(self, request):
        user = json.loads(request.body)

        user["last_login"] = str(timezone.now())

        serializer = self.get_serializer(data=user)
        if serializer.is_valid(raise_exception=True):
            new_user = serializer.create(serializer.validated_data)
            user = models.User(new_user)
            # user.verify_email(request)
            return Response(new_user, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmMailView(APIView):
    """Decodes the confirm account url and activates the account"""

    def get(self, request, token, *args, **kwargs):
        try:
            user = None
        except (TypeError, ValueError, OverflowError, models.User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
        return Response({"detail": "Email Registration Successful"}, status=status.HTTP_200_OK)


class UserProfileView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [CustomTokenAuthentication]
    permissions_classes = [CustomPermission]
    serializer_class = serializers.UserSerializer

    def get(self, request, id, *args, **kwargs):
        user_model = models.User()
        user = user_model.get_user("id", id)

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data

            user_model = models.User()
            user = user_model.update_user(id, data)

            serializer = serializers.UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id, *args, **kwargs):
        user_model = models.User()
        user_model.update_user(id, {"is_active": False})

        return Response({"message": "Account Deactivated"}, status=status.HTTP_204_NO_CONTENT)


class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get("email")

        user_model = models.User()
        user = user_model.get_user("email", email)

        if user:
            token = user["verification_token"]
            reset_url = f"{settings.FRONTEND_RESET_URL}/{token}"
            email_subject = "Password Reset"
            email_message = render_to_string("password_reset_email.html", {"reset_url": reset_url})
            send_mail(email_subject, email_message, settings.EMAIL_FROM, [email], fail_silently=False)
        return Response({"message": "Password reset email sent successfully"}, status=status.HTTP_200_OK)


class PasswordChangeVIew(UpdateAPIView):
    authentication_classes = [CustomTokenAuthentication]
    permissions_classes = [CustomPermission]
    serializer_class = serializers.PasswordChangeSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user_model = models.User()
            token = serializer.validated_data["verification_token"]
            user = user_model.get_user("verification_token", token)
            if user:
                new_password = serializer.validated_data["new_password"]
                new_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
                user_model.update_user(user["id"], {"password": new_password})
                new_verification_token = str(uuid.uuid4())
                user_model.update_user(user["id"], {"verification_token": new_verification_token})
                return Response({"message": "Password Changed Succesfully"}, status=status.HTTP_200_OK)
            return Response({"Error": "Invalid Data"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GoogleAuthException(Exception):
    def __init__(self, error_message):
        self.error_message = error_message
        super().__init__(self.error_message)
        return HttpResponse(self.error_message)


def google_auth(request):
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
        ],
        redirect_uri="http://127.0.0.1:8000/api/users/google/login/callback/",
    )
    authorization_url, _ = flow.authorization_url(prompt="select_account")
    return redirect(authorization_url)


def google_auth_callback(request):
    code = request.GET.get("code")
    try:
        if code:
            flow = Flow.from_client_secrets_file(
                settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
                scopes=[
                    "https://www.googleapis.com/auth/userinfo.profile",
                    "openid",
                    "https://www.googleapis.com/auth/userinfo.email",
                ],
                redirect_uri="http://127.0.0.1:8000/api/users/google/login/callback/",
            )

            flow.fetch_token(code=code)
            response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {flow.credentials.token}"},
            )

            if response.status_code == 200:
                google_profile = response.json()
                email = google_profile.get("email")
                users = db["users"]
                existing_user = users.find_one({"email": email})
                if existing_user:
                    if models.LOGIN_TYPE_GOOGLE == existing_user["login_type"]:
                        token = generate_token(user_id=existing_user["id"])
                        existing_user["last_login"] = timezone.now()
                        users.update_one(
                            {"id": existing_user["id"]}, {"$set": {"last_login": existing_user["last_login"]}}
                        )
                        key = token["key"]
                        return HttpResponse(f"Token: {key}, Message: Login Succesful")
                    return HttpResponse("Invalid Login Method")

                first_name = google_profile.get("given_name")
                last_name = google_profile.get("family_name")
                password = str(uuid.uuid4)
                user_dict = dict(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    user_type="customer",
                    login_type="google",
                    is_active=True,
                    password=password,
                )
                user_model = models.User(user_dict=user_dict)
                user = user_model.add_user()
                token = generate_token(user_id=user["id"])
                user["last_login"] = timezone.now()
                users.update_one({"id": user["id"]}, {"$set": {"last_login": user["last_login"]}})
                key = token["key"]
                return HttpResponse(f"Token: {key}, Message: Login Succesful")
            else:
                raise GoogleAuthException("Couldn't Fetch Data")

            return HttpResponse("Done")

        return HttpResponse("Error")
    except GoogleAuthException:
        pass
