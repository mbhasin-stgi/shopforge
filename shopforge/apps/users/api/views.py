"""User API views."""
from rest_framework import generics, permissions, serializers

from shopforge.apps.users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for the current user's profile."""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "phone_number", "date_joined"]
        read_only_fields = ["id", "email", "role", "date_joined"]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update the current user's profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the authenticated user."""
        return self.request.user