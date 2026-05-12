"""Review serializers."""

from rest_framework import serializers

from shopforge.apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Full review serializer for list and detail views."""

    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "rating",
            "title",
            "body",
            "author_name",
            "is_verified_purchase",
            "created_at",
        ]
        read_only_fields = ["id", "author_name", "is_verified_purchase", "created_at"]

    def get_author_name(self, obj) -> str:
        """Return the reviewer's display name (never expose email)."""
        name = obj.author.get_full_name()
        if name:
            parts = name.split()
            return f"{parts[0]} {parts[-1][0]}." if len(parts) > 1 else parts[0]
        return "Anonymous"


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for submitting a new review."""

    class Meta:
        model = Review
        fields = ["rating", "title", "body"]

    def validate_rating(self, value):
        """Enforce 1–5 range explicitly (field validator already does this, belt-and-braces)."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
