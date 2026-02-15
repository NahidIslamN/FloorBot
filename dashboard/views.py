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
        return Response(
            {
                "success":False,
                "message": f"{str(next(iter(serializer.errors.values()))[0])}",
                                
            },
            status=status.HTTP_400_BAD_REQUEST
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
        return Response(
            {
                "success":False,
                "message": f"{str(next(iter(serializer.errors.values()))[0])}",
                                
            },
            status=status.HTTP_400_BAD_REQUEST
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
    

from django.db.models import Q

class OrdersManagementsAdminView(APIView):
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination

    def get(self, request):
        query = request.GET.get('query', None)
        search = request.GET.get('search', None)

        # Filter orders based on query
        if query is None:
            if search is None:
                orders = OrderTable.objects.all().order_by('-id')
            else:
                orders = OrderTable.objects.filter(
                    Q(user__full_name__icontains=search) | Q(id__icontains=search)| Q(product__product_title__icontains=search)| Q(product__id__icontains=search)
                )

        elif query == "shipped":
            if search is None:
                orders = OrderTable.objects.filter(status="in_transit").order_by('-id')
            else:
                orders = OrderTable.objects.filter(
                    Q(status="in_transit") & (Q(user__full_name__icontains=search) | Q(id__icontains=search)| Q(product__product_title__icontains=search)| Q(product__id__icontains=search)) 
                )

        elif query == "unshipped":
            if search is None:
                orders = OrderTable.objects.filter(status="placed").order_by('-id')
            else:
                orders = OrderTable.objects.filter(
                    Q(status="placed") & (Q(user__full_name__icontains=search) | Q(id__icontains=search)| Q(product__product_title__icontains=search)| Q(product__id__icontains=search)) 
                )
        elif query == "cancelled":
          
            if search is None:
                orders = OrderTable.objects.filter(status="cancelled").order_by('-id')
            else:
                orders = OrderTable.objects.filter(
                    Q(status="cancelled") & (Q(user__full_name__icontains=search) | Q(id__icontains=search)| Q(product__product_title__icontains=search)| Q(product__id__icontains=search)) 
                )
        elif query == "delivered":
            if search is None:
                orders = OrderTable.objects.filter(status="delivered").order_by('-id')
            else:
                orders = OrderTable.objects.filter(
                    Q(status="delivered") & (Q(user__full_name__icontains=search) | Q(id__icontains=search)| Q(product__product_title__icontains=search)| Q(product__id__icontains=search)) 
                )
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

from chat_app.tasks import sent_note_to_user

class OrdersManagementsAdminDetails(APIView):
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
                

                status = serializer.validated_data.get('status')
                if status == 'cancelled':
                    order.status = "cancelled"
                    order.save()
                    return Response(
                        {
                            "success":True,
                            "message":"Order Cancled!"
                        }
                    )
                qty = int(serializer.validated_data.get('quantity')) 
                
                if order.quantity == qty:
                    pass
                else:
                    if order.quantity > qty:
                        order.product.stock_quantity += (order.quantity-qty)
                        order.product.total_salses -= (order.quantity-qty)
                    else:
                        order.product.stock_quantity += (order.quantity-qty)
                        order.product.total_salses -= (order.quantity-qty)
                    
                    order.product.save()

                    
                serializer.save()
                sent_note_to_user.delay(user_id=order.user.id, title=f"Shipment confirmed!", content = "Great news! Your shipment has been confirmed and is on its way. You can track the status anytime from your dashboard. Thank you for choosing us!", note_type='success') 
                return Response(
                    {
                        "success":True,
                        "message":"Shipment confirmed!"
                    }
                )
            return Response(
                {
                    "success":False,
                    "message": f"{str(next(iter(serializer.errors.values()))[0])}",
                                    
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "success":False,
                    "message":"Order not found!",
                }, status=status.HTTP_404_NOT_FOUND
            )


    def patch(self, request, pk):
        try:
            order = OrderTable.objects.get(id = pk)
            serializer = OrderTableSerializerUpdate(instance=order, data = request.data, partial=True)
            if serializer.is_valid():
                qty = int(serializer.validated_data.get('quantity')) 
                if order.quantity == qty:
                    pass
                else:
                    if order.quantity > qty:
                        order.product.stock_quantity += (order.quantity-qty)
                        order.product.total_salses -= (order.quantity-qty)
                    else:
                        order.product.stock_quantity += (order.quantity-qty)
                        order.product.total_salses -= (order.quantity-qty)
                    
                    order.product.save()

                    
                serializer.save()
            return Response(
                {
                    "success":False,
                    "message": f"{str(next(iter(serializer.errors.values()))[0])}",
                                    
                },
                status=status.HTTP_400_BAD_REQUEST
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





