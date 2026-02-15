from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ProductSerializerPublic, CategorisSerializers, OrderSerializers, OrderCreateSerializer, ProductSearchSuggestion, OrderFeedBackSerializer, OrderDelivaryStatusUpdateSerializer
from dashboard.models import Product, Category, OrderTable, CustomUser
from Floor_Bot.pagination import CustomPagination
from Floor_Bot import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from decimal import Decimal

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
        search = request.GET.get('search', None)
        
        if search is None:
            products = Product.objects.order_by('-total_salses')
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
            
        elif search == "newest":
            products = Product.objects.order_by('-created_at')
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
        
        elif search == "best":
            products = Product.objects.order_by('-total_salses')
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

        else:
            products = Product.objects.filter(
                Q(product_title__icontains=search) |
                Q(item_description__icontains=search)
            )
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
        











class SearchSuggestion(APIView):
    def get(self, request):
        products = Product.objects.order_by('-created_at')[0:400]
        serializer = ProductSearchSuggestion(products, many=True)
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
        sub_categories = request.GET.get("sub_categories", None)
        # print(sub_categories)
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
        orders = OrderTable.objects.filter(user=request.user)#.exclude(status="delivered")
   
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
        user = request.user
        serializer = OrderCreateSerializer(data=data)
        if serializer.is_valid():
            try:                
                product = Product.objects.get(id = serializer.validated_data.get('product_id'))             
                qty = serializer.validated_data.get('qty')
                
                price = product.sale_price if product.sale_price > 0 else product.regular_price
                total_amount = (price+product.tax_price )* qty 

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
            amount=int(total_amount * 100),
            currency="gbp",
            description=f"Payment for {product_name}",
            metadata={
                    "product_id": product.id,
                    "user_id": user.id,
                    "qty": qty,

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
                        "success": True,
                        "payment": {
                            "payment_intent_id": intent.id,
                            "client_secret": intent.client_secret,
                            "amount": total_amount,
                            "currency": "usd",
                            "product_name": product_name,
                            "qty": qty
                        },
                        "stripe": {
                            "publishable_key": settings.STRIPE_TEST_PUBLIC_KEY
                        }
                    },
                    status=status.HTTP_200_OK
                )
        
        return Response(
            {
                "success":False,
                "message": f"{str(next(iter(serializer.errors.values()))[0])}",
                                
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def put(self, request):
        serializer = OrderFeedBackSerializer(data = request.data)
        if serializer.is_valid():
            try:
                order = OrderTable.objects.get(id = serializer.validated_data.get('order_id'))
                if order.status != "delivered":
                    return Response(
                        {
                            "success":False,
                            "message":"Product not deleverd yet!"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if order.user == request.user:
                    if order.is_feedbacked:
                        return Response(
                            {
                                "success":False,
                                "message":"already feedback given!"
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    else:
                        order.custormer_feedback = serializer.validated_data.get('feedback')
                        order.is_feedbacked = True
                        order.save()
                        return Response(
                            {
                                "success":True,
                                "message":"successfully feedback sent!"
                            },
                            status=status.HTTP_200_OK
                        )
                else:
                    return Response(
                        {
                            "success":False,
                            "message":"wrong order id!"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            except:
                return Response(
                    {
                        "success":False,
                        "message":"order not found!"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(
            {
                "success":False,
                "message": f"{str(next(iter(serializer.errors.values()))[0])}",
                                
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    


    
    def patch(self, request):
        serializer = OrderDelivaryStatusUpdateSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            try:
                order = OrderTable.objects.get(id=serializer.validated_data.get("order_id"))
                if order.user == user:
                    order.status = serializer.validated_data.get("delivary_status")
                    order.save()
                    return Response(
                        {"success": True, "message": "Successfully Updated!"},
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {"success": False, "message": "This is not your order!"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except OrderTable.DoesNotExist:
                return Response(
                    {"success": False, "message": "Order not found!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"success": False, "message": "Invalid data", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
                










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
            product_id = metadata.get("product_id")    
            paid_amount = Decimal(intent["amount_received"])
            paid_amount_doler = Decimal(paid_amount) / 100

            product = Product.objects.get(id = int(product_id))
            user = CustomUser.objects.get(id = int(metadata.get("user_id")))

            qty = int(metadata.get("qty"))
            
            address_line_i = metadata.get('address_line_i')
            address_line_ii = metadata.get("address_line_ii")
            postal_code = metadata.get("postal_code")
            suburb = metadata.get("suburb")
            state = metadata.get("state")
            city = metadata.get("city")
            country_or_region = metadata.get("country_or_region")

            # #Create your order here .........
            order = OrderTable.objects.create( 
                user = user,
                product = product,
                quantity =qty,
                is_paid = True,
                paid_ammount = paid_amount_doler,
                country_or_region = country_or_region,
                address_line_i = address_line_i,
                address_line_ii = address_line_ii,
                suburb = suburb,
                city = city,
                postal_code = postal_code,
                state = state
                
            )
            order.save()
            product.stock_quantity -= qty
            product.total_salses += qty
            product.save()


        return Response({"status": "ok"}, status=status.HTTP_200_OK)
