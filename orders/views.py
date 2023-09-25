from django.utils import timezone
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from logistics.models import Logistic, LogisticRate
from receivers.models import Receiver
from senders.models import Sender
from users.authentications import CustomTokenAuthentication
from users.permissions import CustomPermission

from . import models, serializers


class OrderCreateView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def post(self, request, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        serializer = serializers.OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_data = serializer.create(serializer.validated_data)

        order_db = models.Order()
        updated_order_data = order_db.update_order(order_data["id"], {"user_id": user["id"]})

        logistics_db = Logistic()
        logistic = logistics_db.get_logistic("id", updated_order_data["logistic_id"])
        if not logistic:
            return Response({"error": "Logistics Not Available"}, status=status.HTTP_400_BAD_REQUEST)

        receiver_id = updated_order_data["receiver_id"]
        sender_id = updated_order_data["sender_id"]

        receiver_db = Receiver()
        receiver = receiver_db.get_receiver("id", receiver_id)

        to_region = receiver["region"]

        sender_db = Sender()
        sender = sender_db.get_sender("id", sender_id)

        from_region = sender["region"]

        logistic_id = logistic["id"]

        logistic_rate_db = LogisticRate()
        logistic_rate = logistic_rate_db.get_logistics_rate_price(
            from_region=from_region, to_region=to_region, logistic_id=logistic_id
        )

        price = logistic_rate[0]["price"]
        print(price)

        order_db = models.Order()
        updated_order_data = order_db.update_order(order_data["id"], {"price": price})

        serializer = serializers.OrderSerializer(data=updated_order_data)
        if serializer.is_valid():
            response_data = {"data": serializer.data, "message": "Order Created Successfully"}
            return Response(response_data, status=status.HTTP_200_OK)

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
            serializer = serializers.OrderSerializer(data=order)
            if serializer.is_valid():
                data = {"data": serializer.data, "message": "Order Updated Successfully"}
                return Response(data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
