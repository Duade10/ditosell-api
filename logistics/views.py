from django.utils import timezone
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.authentications import CustomTokenAuthentication
from users.permissions import CustomPermission

from . import models, serializers


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, serializers
from users.authentications import CustomTokenAuthentication
from users.permissions import CustomPermission
from users.models import USER_TYPE_ADMIN


class LogisticListView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def get(self, request):
        user, _ = self.authentication_classes[0]().authenticate(request)

        logistic_db = models.Logistic()
        data = logistic_db.filter_logistic()
        serializer = serializers.LogisticSerializer(data=data, many=True)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogisticCreateView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def post(self, request, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        if user["user_type"] != USER_TYPE_ADMIN:
            return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = serializers.LogisticSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logistic_data = serializer.create(serializer.validated_data)

        serializer = serializers.LogisticSerializer(data=logistic_data)
        if serializer.is_valid():
            response_data = {"data": serializer.data, "message": "Logistic Created Successfully"}
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogisticDetailView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def get(self, request, id, *args, **kwargs):
        logistic_db = models.Logistic()
        data = logistic_db.get_logistic("id", id)

        serializer = serializers.LogisticSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_200_OK)

    def update(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        if user["user_type"] != USER_TYPE_ADMIN:
            return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = serializers.LogisticSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            logistic_db = models.Logistic()
            logistic = logistic_db.get_logistic("id", id)

            logistic = logistic_db.update_logistic(id, serializer.validated_data)
            logistic = logistic_db.update_logistic(id, {"updated_at": str(timezone.now())})

            data = {"data": logistic, "message": "logistic Updated Successfully"}

            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        if user["user_type"] != USER_TYPE_ADMIN:
            return Response({"error": "You do not have the permission"}, status=status.HTTP_401_UNAUTHORIZED)

        logistic_db = models.Logistic()
        logistic = logistic_db.get_logistic("id", id)

        logistic = logistic_db.update_logistic(id, {"is_active": False, "updated_at": str(timezone.now())})
        serializer = serializers.LogisticSerializer(data=logistic)

        if serializer.is_valid():
            data = {"data": serializer.data, "message": "Logistic set as inactive"}
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogisticRateListView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def get(self, request, logistic_id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        logistic_db = models.Logistic()
        logistic = logistic_db.get_logistic("id", logistic_id)

        if not logistic:
            return Response({"error": "Logistic not found"}, status=status.HTTP_404_NOT_FOUND)

        logistic_rate_db = models.LogisticRate()
        logistic_rates = logistic_rate_db.filter_logistic_rate("logistic_id", logistic_id)

        serializer = serializers.LogisticRateSerializer(logistic_rates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogisticRateCreateView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def post(self, request, logistic_id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        logistic_db = models.Logistic()
        logistic = logistic_db.get_logistic("id", logistic_id)

        if not logistic:
            return Response({"error": "Logistic not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.LogisticRateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            validated_data["logistic_id"] = logistic_id

            logistic_rate_db = models.LogisticRate(validated_data)
            logistic_rate_data = logistic_rate_db.add_logistic_rate()

            serializer = serializers.LogisticRateSerializer(logistic_rate_data)
            return Response(
                {"data": serializer.data, "message": "Logistic Rate Created Successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogisticRateDetailView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def get(self, request, logistic_id, logistic_rate_id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        logistic_db = models.Logistic()
        logistic = logistic_db.get_logistic("id", logistic_id)

        if not logistic:
            return Response({"error": "Logistic not found"}, status=status.HTTP_404_NOT_FOUND)

        logistic_rate_db = models.LogisticRate()
        logistic_rate = logistic_rate_db.get_logistic_rate("id", logistic_rate_id)

        if not logistic_rate:
            return Response({"error": "Logistic Rate not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.LogisticRateSerializer(logistic_rate)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, logistic_id, logistic_rate_id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        logistic_db = models.Logistic()
        logistic = logistic_db.get_logistic("id", logistic_id)

        if not logistic:
            return Response({"error": "Logistic not found"}, status=status.HTTP_404_NOT_FOUND)

        logistic_rate_db = models.LogisticRate()
        logistic_rate = logistic_rate_db.get_logistic_rate("id", logistic_rate_id)

        if not logistic_rate:
            return Response({"error": "Logistic Rate not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.LogisticRateSerializer(logistic_rate, data=request.data)
        if serializer.is_valid(raise_exception=True):
            updated_logistic_rate_data = logistic_rate_db.update_logistic_rate(
                logistic_rate_id, serializer.validated_data
            )
            updated_serializer = serializers.LogisticRateSerializer(updated_logistic_rate_data)
            return Response(
                {"data": updated_serializer.data, "message": "Logistic Rate Updated Successfully"},
                status=status.HTTP_200_OK,
            )

    def delete(self, request, logistic_id, logistic_rate_id, *args, **kwargs):
        user, _ = self.authentication_classes[0]().authenticate(request)

        logistic_db = models.Logistic()
        logistic = logistic_db.get_logistic("id", logistic_id)

        if not logistic:
            return Response({"error": "Logistic not found"}, status=status.HTTP_404_NOT_FOUND)

        logistic_rate_db = models.LogisticRate()
        logistic_rate = logistic_rate_db.get_logistic_rate("id", logistic_rate_id)

        if not logistic_rate:
            return Response({"error": "Logistic Rate not found"}, status=status.HTTP_404_NOT_FOUND)

        logistic_rate_db.delete_logistic_rate(logistic_rate_id)
        return Response({"message": "Logistic Rate Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)
