"""Address API views — authenticated users manage their own addresses."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from shopforge.apps.addresses.api.serializers import UserAddressSerializer
from shopforge.apps.addresses.models import UserAddress


class UserAddressViewSet(viewsets.ModelViewSet):
    """
    CRUD for the authenticated user's saved shipping addresses.

    list:     GET /api/addresses/
    create:   POST /api/addresses/
    retrieve: GET /api/addresses/{id}/
    update:   PUT/PATCH /api/addresses/{id}/
    destroy:  DELETE /api/addresses/{id}/
    """

    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Users only see their own addresses."""
        return UserAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Associate the new address with the current user."""
        serializer.save(user=self.request.user)
