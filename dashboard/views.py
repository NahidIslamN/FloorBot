from .models import Product, Images, Category
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import ProductSerializer


# Create your views here.

class Catalogs_Views(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        products = Product.objects.all().order_by("-id")
        serializer = ProductSerializer(products, many=True)

        return Response(
            {
                "success":True,
                "message":"data fatched!",
                "products":serializer.data
            }, status= status.HTTP_200_OK)
    
    def post(self, request):

        serializer = ProductSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                    {
                    "success":True,
                    "message":"Product Created!",
                    "product_details":serializer.data
                    }
                )
        else:
            return Response(
                {
                    "success":False,
                    "message":"Required Field Mising!",
                    "errors":serializer.errors
                }
            )

    def put(self, request, pk):

        try:
            product = Product.objects.get(id=pk)
        except:
            return Response({
                "success":False,
                "message":"Product not found !"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(instance = product, data = request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                    {
                    "success":True,
                    "message":"Product Updated!",
                    "product_details":serializer.data
                    }
                )
        else:
            return Response(
                {
                    "success":False,
                    "message":"Required Field Mising!",
                    "errors":serializer.errors
                }
            )

    def delete(self, request, pk):

        try:
            product = Product.objects.get(id=pk)
            product.delete()
            return Response(
                    {
                    "success":True,
                    "message":"Product deleted!",
                    },
                    status=status.HTTP_200_OK
                )
        except:
            return Response({
                "success":False,
                "message":"Product not found !"
            }, status=status.HTTP_404_NOT_FOUND)




