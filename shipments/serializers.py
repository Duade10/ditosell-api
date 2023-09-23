from rest_framework import serializers

from . import models


class ShipmentSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=40, required=False, read_only=True)
    category = serializers.CharField(max_length=50, required=True)
    item = serializers.CharField(max_length=100, required=True)
    weight = serializers.FloatField(required=True)
    quantity = serializers.IntegerField(required=True)
    image = serializers.ImageField(required=False)
    sender_id = serializers.CharField(max_length=40, required=True)
    receiver_id = serializers.CharField(max_length=40, required=True)
    user_id = serializers.CharField(max_length=40, required=False)
    created_at = serializers.DateTimeField(required=False)
    created_at = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        shipment = models.Shipment(shipment_dict=validated_data)
        new_shipment = shipment.add_shipment()
        return new_shipment
