from rest_framework import serializers

from app.rental.models import RentalRequest, RentalRequestItem


class RentalRequestItemSerializer(serializers.ModelSerializer):
    device_id = serializers.IntegerField(
        source="device.id",
        read_only=True
    )

    device_name = serializers.CharField(
        source="device.name",
        read_only=True
    )

    class Meta:
        model = RentalRequestItem
        fields = [
            "id",
            "device",
            "device_id",
            "device_name",
            "quantity",
            "return_date",
        ]
        read_only_fields = [
            "id",
            "device_id",
            "device_name",
        ]


class RentalRequestSerializer(serializers.ModelSerializer):
    items = RentalRequestItemSerializer(many=True)

    class Meta:
        model = RentalRequest
        fields = [
            "id",
            "student",
            "full_name",
            "group",
            "discipline",
            "status",
            "issue_date",
            "created_at",
            "items",
        ]
        read_only_fields = ["id", "student", "status", "issue_date", "created_at"]