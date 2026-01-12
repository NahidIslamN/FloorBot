from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ProductSerializerPublic, CategorisSerializers
from dashboard.models import Product, Category, OrderTable
from .pagination import CustomPagination


class Categoriesview(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorisSerializers(categories, many=True)
        return Response(
            {
                "success":True,
                "message":"data fatched",
                "categories":serializer.data
            }
        )


class ProductsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        products = Product.objects.all().order_by('-id')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(products, request)
        if page is not None:
            serializer = ProductSerializerPublic(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ProductSerializerPublic(products, many=True)
        return Response({
            "success": True,
            "message": "Data fetched successfully!",
            "data": serializer.data
        })


class NewestProducts(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        products = Product.objects.all().order_by('-created_at')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(products, request)
        if page is not None:
            serializer = ProductSerializerPublic(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ProductSerializerPublic(products, many=True)
        return Response({
            "success": True,
            "message": "Data fetched successfully!",
            "data": serializer.data
        })


class BestProducts(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        products = Product.objects.all().order_by('-total_salses')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(products, request)
        if page is not None:
            serializer = ProductSerializerPublic(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ProductSerializerPublic(products, many=True)
        return Response({
            "success": True,
            "message": "Data fetched successfully!",
            "data": serializer.data
        })


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializerPublic(product)
            return Response({
                "success": True,
                "message": "Product details fetched!",
                "data": serializer.data
            })
        except Product.DoesNotExist:
            return Response({
                "success": False,
                "message": "Product not found!"
            }, status=status.HTTP_404_NOT_FOUND)


class CategoryProductsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request, category_id):
        products = Product.objects.filter(main_category_id=category_id).order_by('-id')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(products, request)
        if page is not None:
            serializer = ProductSerializerPublic(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ProductSerializerPublic(products, many=True)
        return Response({
            "success": True,
            "message": "Data fetched successfully!",
            "data": serializer.data
        })


class My_Confirmed_Ordedrs(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get(self, request):
        orders = OrderTable.objects.filter(user = request.user)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(orders, request)
        if page is not None:
            serializer = ProductSerializerPublic(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        pass

    def post(self, request):
        pass