from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=40, required=False)
    reference = serializers.CharField(max_length=255)
    currency = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_expected = serializers.DecimalField(max_digits=10, decimal_places=2)
    fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField(max_length=20)
    payment_reference = serializers.CharField(max_length=255)
    transaction_status = serializers.CharField(max_length=20)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        payment = Payment(**validated_data)
        new_payment = payment.add_payment()
        return new_payment
