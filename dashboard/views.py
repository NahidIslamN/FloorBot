from .models import Product, Images, Category
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .serializers import ProductSerializer, CustoerFeedBack, OrderTableSerializerView, OrderTableSerializerUpdate
import stripe
from Floor_Bot import settings
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
from .models import OrderTable
from Floor_Bot.pagination import CustomPagination



# Create your views here.

class HomePage(APIView):
    def get(self, request):

        return Response(
            {
                "message":"Hello World!"
            }
        )
    


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



class CustomerFeedBacke(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        feedbacks = OrderTable.objects.filter(is_feedbacked = True).order_by('-id')[0:500]
        serializer = CustoerFeedBack(feedbacks, many=True)
        return Response(
            {
                "success":True,
                "message":"customer feedback!",
                "feedbacks":serializer.data
            }
        )
    



class OrdersManagementsAdmin(APIView):
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination

    def get(self, request):
        query = request.GET.get('query', None)

        # Filter orders based on query
        if query is None:
            orders = OrderTable.objects.all().order_by('-id')
        elif query == "shipped":
            orders = OrderTable.objects.filter(status="in_transit").order_by('-id')
        elif query == "unshipped":
            orders = OrderTable.objects.filter(status="placed").order_by('-id')
        elif query == "cancelled":
            orders = OrderTable.objects.filter(status="cancelled").order_by('-id')
        elif query == "delivered":
            orders = OrderTable.objects.filter(status="delivered").order_by('-id')
        else:
            return Response(
                {
                    "success": False,
                    "message": "Invalid query parameter. Use 'shipped', 'unshipped', or 'cancelled'.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Pagination
        paginator = self.pagination_class()
        paginated_orders = paginator.paginate_queryset(orders, request)
        serializer = OrderTableSerializerView(paginated_orders, many=True)

        return paginator.get_paginated_response({
            "success": True,
            "message": "Orders fetched successfully.",
            "orders": serializer.data
        })



class OrdersManagementsAdmin(APIView):
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination

    def get(self, request, pk):
        try:
            order = OrderTable.objects.get(id = pk)
            serializer = OrderTableSerializerView(order)
            return Response(
                {
                    "success":True,
                    "message":"",
                    "order_data":serializer.data
                },
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {
                    "success":False,
                    "message":"Order not found!",
                    
                }, status=status.HTTP_404_NOT_FOUND
            )
    

    def put(self, request, pk):
        try:
            order = OrderTable.objects.get(id = pk)
            serializer = OrderTableSerializerUpdate(instance=order, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
            return Response(
                {
                    "success":True,
                    "message":"",
                    "order_data":serializer.data
                },
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {
                    "success":False,
                    "message":"Order not found!",
                }, status=status.HTTP_404_NOT_FOUND
            )


      



######################## wallet section ###################################

class StripeWalletBalance(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):            
        balance = stripe.Balance.retrieve()
        available_amount = 0
        pending_amount = 0
        currency=None
        if balance['available']:
            available_amount = balance['available'][0]['amount'] / 100
            currency = balance['available'][0]['currency']

        if balance['pending']:
            pending_amount = balance['pending'][0]['amount'] / 100

        return Response({
            "success": True,
            "total_balance": available_amount,
            "pending_amount": pending_amount,
            "currency": currency
        },
        status=status.HTTP_200_OK
    )





