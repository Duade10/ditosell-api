from django.utils import timezone
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from users import CustomPermission, CustomTokenAuthentication

from . import models, serializers


class PaymentCreateView(CreateAPIView):
    def create(self, request, *args, **kwargs):
        data = request.data.get("data")

        if not data:
            return Response({"error": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.PaymentSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            order_id = data.get("payment_reference")
            user, _ = self.authentication_classes[0]().authenticate(request)

            payment_db = models.Payment()

            payment = payment_db.get_payment("payment_reference", order_id)

            if payment is None:
                return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

            payment = payment_db.update_payment(order_id, serializer.validated_data)
            payment = payment_db.update_payment(order_id, {"updated_at": str(timezone.now())})
            serializer = serializers.PaymentSerializer(data=payment)
            if serializer.is_valid():
                data = {"data": serializer.data, "message": "Payment Updated Successfully"}
                return Response(data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentDetailView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def get(self, request, order_id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)
        payment_db = models.Payment()
        data = payment_db.get_payment("payment_reference", order_id)
        if data is None:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        if data["user_id"] != user["id"]:
            return Response({"error": "You do not have permission"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = serializers.PaymentSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
