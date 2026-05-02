from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import (
    IsAdminOrManager,
    IsAdminOrManagerOrReadOnly,
    IsOwnerOrReadOnly,
    IsOwnerOrAdmin,
)
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class CategoryListCreateView(APIView):
    permission_classes = [IsAdminOrManagerOrReadOnly]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CategoryDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminOrManager()]
        return [IsAdminOrManagerOrReadOnly]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({"error": "Категория не найдена"}, status= status.HTTP_404_NOT_FOUND)

        