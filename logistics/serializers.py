from rest_framework import serializers

from . import models


class LogisticSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=40, required=False)
    image = serializers.CharField(required=False)
    name = serializers.CharField(max_length=40, required=True)
    is_active = serializers.BooleanField(required=False)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        validated_data.pop("id", None)
        validated_data.pop("is_active", None)
        validated_data.pop("created_at", None)
        validated_data.pop("updated_at", None)

        logistic = models.Logistic(logistic_dict=validated_data)
        new_logistic = logistic.add_logistic()
        return new_logistic


class LogisticRateSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=40, read_only=True)
    from_region = serializers.CharField(max_length=255, required=True)
    to_region = serializers.CharField(max_length=255, required=True)
    price = serializers.FloatField(required=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    logistic_id = serializers.CharField(max_length=40, required=True)

    def create(self, validated_data):
        logistic_rate = models.LogisticRate(**validated_data)
        logistic_rate.save()
        return logistic_rate
