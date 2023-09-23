from django.utils import timezone
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.authentications import CustomTokenAuthentication
from users.permissions import CustomPermission

from . import models, serializers


class ShipmentCreateView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    serializer_class = serializers.ShipmentSerializer

    def post(self, request, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        data = request.data
        serializer = serializers.ShipmentSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            data = serializer.create(serializer.validated_data)
            shipment_db = models.Shipment()
            data = shipment_db.update_shipment(data["id"], {"user_id": user["id"]})

            data = {"data": data, "message": "Shipment Created Successfully"}
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


class ShipmentDetailView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def get(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)
        shipment_db = models.Shipment()
        data = shipment_db.get_shipment("id", id)
        if data["user_id"] != user["id"]:
            return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        data = request.data
        serializer = serializers.ShipmentSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            shipment_db = models.Shipment()
            shipment = shipment_db.get_shipment("id", id)

            if shipment["user_id"] != user["id"]:
                return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)

            shipment = shipment_db.update_shipment(id, serializer.validated_data)
            shipment = shipment_db.update_shipment(id, {"updated_at": str(timezone.now())})
            data = {"data": shipment, "message": "Shipment Updated Successfully"}
            return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        data = request.data

        shipment_db = models.Shipment()
        shipment = shipment_db.get_shipment("id", id)

        if shipment["user_id"] != user["id"]:
            return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)

        shipment = shipment_db.update_shipment(id, {"is_active": False, "updated_at": str(timezone.now())})
        data = {"data": shipment, "message": "Shipment set as inactive"}
        return Response(data, status=status.HTTP_200_OK)
