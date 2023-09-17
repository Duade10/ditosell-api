from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    path("<int:id>/", views.UserProfileView.as_view(), name="detail"),
]
