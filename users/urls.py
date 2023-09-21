from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("<str:id>/", views.UserProfileView.as_view(), name="detail"),
    path("password/change/", views.PasswordChangeVIew.as_view(), name="change_password"),
    path("auth/google/", views.google_auth, name="google_auth"),
    path("google/login/callback/", views.google_auth_callback, name="google_callback"),
]
