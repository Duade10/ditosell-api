from django.utils import timezone
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.authentications import CustomTokenAuthentication
from users.permissions import CustomPermission

from . import models, serializers


class ReceiverCreateView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def post(self, request, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        data = request.data
        serializer = serializers.ReceiverSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.create(serializer.validated_data)
            receiver_db = models.Receiver()
            data = receiver_db.update_receiver(data["id"], {"user_id": user["id"]})
            data = {"data": data, "message": "Receiver Created Successfully"}

            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReceiverDetailView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def get(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)
        receiver_db = models.Receiver()
        data = receiver_db.get_receiver("id", id)
        if data["user_id"] != user["id"]:
            return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        data = request.data
        serializer = serializers.ReceiverSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            receiver_db = models.Receiver()
            receiver = receiver_db.get_receiver("id", id)

            if receiver["user_id"] != user["id"]:
                return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)

            receiver = receiver_db.update_receiver(id, serializer.validated_data)
            receiver = receiver_db.update_receiver(id, {"updated_at": str(timezone.now())})
            data = {"data": receiver, "message": "Receiver Updated Successfully"}
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        data = request.data

        receiver_db = models.Receiver()
        receiver = receiver_db.get_receiver("id", id)

        if receiver["user_id"] != user["id"]:
            return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)

        receiver = receiver_db.update_receiver(id, {"is_active": False, "updated_at": str(timezone.now())})
        data = {"data": receiver, "message": "Receiver set as inactive"}
        return Response(data, status=status.HTTP_200_OK)
