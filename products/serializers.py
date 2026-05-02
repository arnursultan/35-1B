from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]

class ProductSerializer(serializers.ModelSerializer):
    owner_email = serializers.SerializerMethodField
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )

    class Meta:
        fields = [
            "id", "name", "description", "price",
            "stock", "category", "category_id",
            "owner_email", "is_active", "created_at",
        ]
        read_only_fields = ["id", "owner_email", "created_at"]

    def get_owner_email(self, obj):
        return obj.owner.email

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)