from rest_framework import serializers

from . import models


class ReceiverSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=70, required=True)
    phone_number = serializers.CharField(max_length=20, required=True)
    pickup_address = serializers.CharField(required=True)
    region = serializers.ChoiceField(choices=models.REGION_TYPE, required=True)
    user_id = serializers.CharField(read_only=True, max_length=40, required=False)
    sender_id = serializers.CharField(max_length=40, required=True)
    created_at = serializers.DateTimeField(read_only=True, required=False)
    updated_at = serializers.DateTimeField(read_only=True, required=False)

    def create(self, validated_data):
        receiver = models.Receiver(receiver_dict=validated_data)
        new_receiver = receiver.add_receiver()
        return new_receiver
