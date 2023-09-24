from rest_framework import serializers

from receivers.serializers import ReceiverSerializer
from receivers.models import Receiver
from senders.models import Sender
from senders.serializers import SenderSerializer
from shipments.models import Shipment
from shipments.serializers import ShipmentSerializer

from . import models


class OrderSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=40, required=False)
    user_id = serializers.CharField(max_length=40, required=False)
    progress = serializers.CharField(required=False)
    is_active = serializers.BooleanField(default=True)
    logistics = serializers.CharField(max_length=40, required=True)
    sender_id = serializers.CharField(max_length=40, write_only=True, required=True)
    sender = serializers.SerializerMethodField()
    receiver_id = serializers.CharField(max_length=40, write_only=True, required=True)
    receiver = serializers.SerializerMethodField()
    shipment_id = serializers.CharField(max_length=40, write_only=True, required=True)
    shipment = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        order = models.Order(order_dict=validated_data)
        new_order = order.add_order()
        return new_order

    def get_sender(self, obj):
        sender_id = obj.get("sender_id")
        sender_db = Sender()
        sender_data = sender_db.get_sender("id", sender_id)
        serializer = SenderSerializer(sender_data)
        return serializer.data

    def get_receiver(self, obj):
        receiver_id = obj.get("receiver_id")
        receiver_db = Receiver()
        receiver_data = receiver_db.get_receiver("id", receiver_id)
        serializer = ReceiverSerializer(receiver_data)
        return serializer.data

    def get_shipment(self, obj):
        shipment_id = obj.get("shipment_id")
        shipment_db = Shipment()
        shipment_data = shipment_db.get_shipment("id", shipment_id)
        serializer = ShipmentSerializer(shipment_data)
        return serializer.data
