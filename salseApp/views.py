from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ProductSerializerPublic, CategorisSerializers, OrderSerializers, OrderCreateSerializer
from dashboard.models import Product, Category, OrderTable
from .pagination import CustomPagination
from Floor_Bot import settings

import stripe
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY



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



class User_Complete_Ordedrs(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get(self, request):
        orders = OrderTable.objects.filter(user = request.user, status="delivered")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(orders, request)
        if page is not None:
            serializer = OrderSerializers(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = OrderSerializers(orders, many=True)
        return Response({
            "success": True,
            "message": "Data fetched successfully!",
            "data": serializer.data
        })





class User_Ordedrs(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get(self, request):
        orders = OrderTable.objects.filter(user = request.user)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(orders, request)
        if page is not None:
            serializer = OrderSerializers(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = OrderSerializers(orders, many=True)
        return Response({
            "success": True,
            "message": "Data fetched successfully!",
            "data": serializer.data
        })

    def post(self, request):
        data = request.data

        serializer = OrderCreateSerializer(data=data)
        if serializer.is_valid():
            try:
                user = request.user
                product = Product.objects.get(id = serializer.validated_data.get('product_id'))             
                qty = serializer.validated_data.get('qty')
                delivery_charge = serializer.validated_data.get("delivery_charge")
                tax_charge = serializer.validated_data.get('tax_charge')

                ammount = product.sale_price
                ammount2 = product.regular_price
                total_ammount = 0

                if ammount>0:
                    ammount = ammount*qty
                else:
                    ammount = ammount2*qty

                total_ammount = ammount+delivery_charge+tax_charge
            

                country_or_region = serializer.validated_data.get('country_or_region')
                address_line_i = serializer.validated_data.get('address_line_i')
                address_line_ii = serializer.validated_data.get('address_line_ii')
                suburb = serializer.validated_data.get('suburb')
                city = serializer.validated_data.get('city')
                postal_code = serializer.validated_data.get('postal_code')
                state = serializer.validated_data.get('state')
               
            
            except Exception as e:
                return Response(
                    {
                        "success":True,
                        "message":"validation errors!",
                        "errors":f"{e}"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


            product_name = product.product_title
           
            intent = stripe.PaymentIntent.create(
            amount=int(total_ammount * 100),
            currency="usd",
            description=f"Payment for {product_name}",
            metadata={
                    "product_iid": product.id,
                    "user_id": user.id,
                    "qty": qty,
                    "delevary_charge": delivery_charge,
                    "tax_charge":tax_charge,

                    #address info
                    "country_or_region" : country_or_region,
                    "address_line_i":address_line_i,
                    "address_line_ii":address_line_ii,
                    "suburb":suburb,
                    "city":city,
                    "postal_code":postal_code,
                    "state":state
                }

            )
     
            return Response(
                    {
                        "client_secret": intent.client_secret,
                        "publishable_key":settings.STRIPE_TEST_PUBLIC_KEY
                    }
                
                )






from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import stripe
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookDebugAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        if not sig_header:
            return Response(
                {"error": "Stripe-Signature header missing"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=settings.STRIPE_WEBHOCK_SECRET
            )
        except stripe.error.SignatureVerificationError as e:
            return Response(
                {"error": "Signature verification failed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response(
                {"error": "Invalid payload"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]
            metadata = dict(intent.metadata)
            print("📦 METADATA:", json.dumps(metadata, indent=2))

        return Response({"status": "ok"}, status=status.HTTP_200_OK)
