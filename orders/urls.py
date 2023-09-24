from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("create/", views.OrderCreateView.as_view(), name="create"),
    path("detail/<str:id>/", views.OrderDetailView.as_view(), name="detail"),
]
