"""Address serializers."""

from rest_framework import serializers

from shopforge.apps.addresses.models import UserAddress


class UserAddressSerializer(serializers.ModelSerializer):
    """Full address serializer for CRUD operations."""

    class Meta:
        model = UserAddress
        fields = [
            "id",
            "label",
            "full_name",
            "line1",
            "line2",
            "city",
            "state",
            "postal_code",
            "country",
            "phone",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
