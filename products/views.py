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
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({"error": "Категория не найдена"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        category = self.get_object(pk)
        return Response({"error": "Категория не наайдена"}, status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductListCreateView(APIView):
    permissions_classes = [IsAdminOrManagerOrReadOnly]

    def get(self, request):
        products = Product.objects.filter(is_active=True).select_related("owner", "category")
        serializer = ProductSerializer(products, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProductDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT"):
            return [IsOwnerOrAdmin()]
        if self.request.method == "DELETE":
            return [IsAdminOrManager()]
        return [IsAuthenticated()]

    def get_object(self, pk, request):
        try:
            obj = Product.objects.get(pk=pk)
            self.check_object_permissions(request, obj)
            return obj
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = Product.objects.filter(pk=pk).select_related("owner", "category").first()
        if not product:
            return Response({"error": "Продукт не найден"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, context={"request": request})
        return Response(serializer.data)

    def patch(self, request,pk):
        product = self.get_object(pk, request)
        if not product:
            return Response({"error": "Продукт не найден"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(
            product, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request,pk):
        product = self.get_object(pk, request)
        if not product:
            return Response({"error": "Продукт не найден"}, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MyProductView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.all(
            owner=request.user
        ).select_related("category")
        serializer = ProductSerializer(products, many=True, context={"request": request})
        return Response(serializer.data)