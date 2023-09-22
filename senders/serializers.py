from rest_framework import serializers
from . import models


class SenderSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=70, required=True)
    phone_number = serializers.CharField(max_length=20, required=True)
    pickup_address = serializers.CharField(required=True)
    region = serializers.ChoiceField(choices=models.REGION_TYPE, required=True)

    def create(self, validated_data):
        sender = models.Sender(sender_dict=validated_data)
        new_sender = sender.add_sender()
        return new_sender
