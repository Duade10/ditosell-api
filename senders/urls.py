from django.urls import path

from . import views

app_name = "senders"

urlpatterns = [
    path("create/", views.SenderCreateView.as_view(), name="create"),
    path("detail/<str:id>/", views.SenderDetailView.as_view(), name="detail"),
]
