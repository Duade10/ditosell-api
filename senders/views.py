from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status

from users.authentications import CustomTokenAuthentication
from users.permissions import CustomPermission

from . import models, serializers


class SenderCreateView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def post(self, request, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        data = request.data
        serializer = serializers.SenderSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.create(serializer.validated_data)

            sender_db = models.Sender()
            data = sender_db.update_sender(data["id"], {"user_id": user["id"]})
            data = {"data": data, "message": "Sender Created Successfully"}

            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SenderDetailView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def get(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        sender_db = models.Sender()
        data = sender_db.get_sender("id", id)
        if data["user_id"] != user["id"]:
            return Response({"Error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        data = request.data
        serializer = serializers.SenderSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            sender_db = models.Sender()
            sender = sender_db.get_sender("id", id)

            if sender["user_id"] != user["id"]:
                return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)

            sender = sender_db.update_sender(id, serializer.validated_data)
            data = {"data": sender, "message": "Sender Updated Successfully"}
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        data = request.data

        sender_db = models.Sender()
        sender = sender_db.get_sender("id", id)

        if sender["user_id"] != user["id"]:
            return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)

        sender = sender_db.update_sender(id, {"is_active": False})
        data = {"data": sender, "message": "Sender set as inactive"}
        return Response(data, status=status.HTTP_200_OK)
