from django.utils import timezone
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.authentications import CustomTokenAuthentication
from users.permissions import CustomPermission

from . import models, serializers


class OrderCreateView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def post(self, request, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        data = request.data
        serializer = serializers.OrderSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.create(serializer.validated_data)

            order_db = models.Order()

            data = order_db.update_order(data["id"], {"user_id": user["id"]})
            serializer = serializers.OrderSerializer(data=data)
            if serializer.is_valid():
                data = {"data": serializer.data, "message": "Order Created Successfully"}

                return Response(data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def get(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)
        order_db = models.Order()
        data = order_db.get_order("id", id)
        if data["user_id"] != user["id"]:
            return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = serializers.OrderSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_200_OK)

    def update(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        data = request.data
        serializer = serializers.OrderSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            order_db = models.Order()
            order = order_db.get_order("id", id)

            if order["user_id"] != user["id"]:
                return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)

            order = order_db.update_order(id, serializer.validated_data)
            order = order_db.update_order(id, {"updated_at": str(timezone.now())})
            data = {"data": order, "message": "Order Updated Successfully"}
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        data = request.data

        order_db = models.Order()
        order = order_db.get_order("id", id)

        if order["user_id"] != user["id"]:
            return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)

        order = order_db.update_order(id, {"is_active": False, "updated_at": str(timezone.now())})
        data = {"data": order, "message": "Order set as inactive"}
        return Response(data, status=status.HTTP_200_OK)
