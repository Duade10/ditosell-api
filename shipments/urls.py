from django.urls import path

from . import views

app_name = "shipments"

urlpatterns = [
    path("create/", views.ShipmentCreateView.as_view(), name="create"),
    path("detail/<str:id>/", views.ShipmentDetailView.as_view(), name="detail"),
]
