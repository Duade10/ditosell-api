from django.urls import path

from . import views

app_name = "receivers"

urlpatterns = [
    path("create/", views.ReceiverCreateView.as_view(), name="create"),
    path("detail/<str:id>/", views.ReceiverDetailView.as_view(), name="detail"),
]
