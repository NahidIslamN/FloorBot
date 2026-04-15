from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ProductSerializerPublic, CategorisSerializers, OrderSerializers, OrderCreateSerializer,OrderCreateSerializerV2, ProductSearchSuggestion, OrderFeedBackSerializer, OrderDelivaryStatusUpdateSerializer
from dashboard.models import Product, Category, OrderTable, OrderItem, CustomUser
from Floor_Bot.pagination import CustomPagination
from Floor_Bot import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.db import transaction
from decimal import Decimal
import json
import logging

import stripe
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

logger = logging.getLogger(__name__)



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
        logger.info("👤 User_Ordedrs endpoint: user=%s, user.id=%s, is_authenticated=%s", user, user.id if hasattr(user, 'id') else 'NO_ID', user.is_authenticated if hasattr(user, 'is_authenticated') else 'N/A')
        serializer = OrderCreateSerializer(data=data)
        if serializer.is_valid():
            try:                
                product = Product.objects.get(id = serializer.validated_data.get('product_id'))             
                qty = serializer.validated_data.get('qty')
                
                price = product.sale_price if product.sale_price > 0 else product.regular_price
                total_amount = (price+product.tax_price)* qty

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
                    "product_id": str(product.id),
                    "user_id": str(user.id),
                    "qty": str(qty),
                    "items": json.dumps([{"product_id": int(product.id), "qty": int(qty)}]),
                    "source": "flor_bot_orders",

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
                


def _parse_order_items_from_metadata(metadata):
    """Parse Stripe metadata into a normalized list of order items."""
    if metadata.get("items"):
        try:
            raw_items = json.loads(metadata.get("items"))
            return [
                {"product_id": int(item["product_id"]), "qty": int(item["qty"])}
                for item in raw_items
            ]
        except Exception:
            pass

    if metadata.get("products"):
        try:
            raw_items = json.loads(metadata.get("products"))
            return [
                {"product_id": int(item["product_id"]), "qty": int(item["qty"])}
                for item in raw_items
            ]
        except Exception:
            pass

    if metadata.get("product_id") and metadata.get("qty"):
        return [{"product_id": int(metadata.get("product_id")), "qty": int(metadata.get("qty"))}]

    return []


def _resolve_user_id_from_metadata(metadata):
    logger.info("📋 Metadata received: %s", metadata)
    user_id = metadata.get("user_id") or metadata.get("user") or metadata.get("uid")
    if user_id in [None, "", "None"]:
        logger.warning("⚠️ user_id is None/empty in metadata")
        return None
    return int(user_id)


def _is_flor_bot_order_intent(metadata):
    """Check if this payment intent was created by the Flor Bot app."""
    source = metadata.get("source")
    result = source == "flor_bot_orders"
    logger.debug("🔍 Source check: source=%s, is_flor_bot=%s", source, result)
    return result


def _create_order_from_payment_metadata(metadata, paid_amount_doler, payment_intent_id=None):
    """Create an OrderTable and related OrderItem rows from Stripe metadata."""
    logger.info("🔄 Starting order creation from metadata. payment_intent_id=%s, amount=%.2f", payment_intent_id, paid_amount_doler)
    items_data = _parse_order_items_from_metadata(metadata)
    if not items_data:
        logger.warning("❌ Webhook skipped: no valid order items in metadata. Available keys: %s", list(metadata.keys()))
        return None

    user_id = _resolve_user_id_from_metadata(metadata)
    if user_id is None:
        logger.warning("❌ Webhook skipped: missing user_id in Stripe metadata. Keys: %s", list(metadata.keys()))
        return None

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        logger.warning("❌ Webhook skipped: user not found for user_id=%s", user_id)
        return None

    if payment_intent_id and OrderTable.objects.filter(tracking_no=payment_intent_id).exists():
        logger.info("⏭️ Order already exists for payment_intent=%s, returning existing order", payment_intent_id)
        return OrderTable.objects.get(tracking_no=payment_intent_id)

    address_line_i = metadata.get("address_line_i")
    address_line_ii = metadata.get("address_line_ii")
    postal_code = metadata.get("postal_code")
    suburb = metadata.get("suburb")
    state = metadata.get("state")
    city = metadata.get("city")
    country_or_region = metadata.get("country_or_region")

    with transaction.atomic():
        order = OrderTable.objects.create(
            user=user,
            is_paid=True,
            paid_ammount=paid_amount_doler,
            order_total=paid_amount_doler,
            tracking_no=payment_intent_id,
            country_or_region=country_or_region,
            address_line_i=address_line_i,
            address_line_ii=address_line_ii,
            suburb=suburb,
            city=city,
            postal_code=postal_code,
            state=state,
        )

        for item in items_data:
            product = Product.objects.select_for_update().get(id=item["product_id"])
            qty = int(item["qty"])
            price = product.sale_price if product.sale_price > 0 else product.regular_price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=price,
                tax=product.tax_price,
            )

            product.stock_quantity -= qty
            product.total_salses += qty
            product.save()
        
        order.save()

    logger.info("✅ Order successfully created: order_id=%s, user_id=%s, items=%d, total=%.2f", order.id, user.id, len(items_data), paid_amount_doler)
    return order


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
            logger.info("✅ Webhook event received - payment_intent_id: %s", intent.get("id"))
            logger.info("📦 Payment metadata: %s", metadata)
            if not _is_flor_bot_order_intent(metadata):
                logger.info("Webhook ignored: non-app payment intent (source=%s)", metadata.get("source"))
                return Response({"status": "ignored"}, status=status.HTTP_200_OK)
            paid_amount = Decimal(intent["amount_received"])
            paid_amount_doler = Decimal(paid_amount) / 100
            logger.info("💰 Processing order: amount=%.2f, payment_intent=%s", paid_amount_doler, intent.get("id"))
            try:
                order = _create_order_from_payment_metadata(
                    metadata,
                    paid_amount_doler,
                    payment_intent_id=intent.get("id")
                )
                logger.info("✨ Order created successfully: order_id=%s", order.id if order else "None")
            except Exception as e:
                logger.warning("Webhook order creation skipped: %s", str(e))


        return Response({"status": "ok"}, status=status.HTTP_200_OK)





@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookDebugAPIViewV2(APIView):
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
            logger.info("✅ Webhook V2 event received - payment_intent_id: %s", intent.get("id"))
            logger.info("📦 Payment metadata: %s", metadata)
            if not _is_flor_bot_order_intent(metadata):
                logger.info("Webhook V2 ignored: non-app payment intent (source=%s)", metadata.get("source"))
                return Response({"status": "ignored"}, status=status.HTTP_200_OK)
            paid_amount = Decimal(intent["amount_received"])
            paid_amount_doler = Decimal(paid_amount) / 100
            logger.info("💰 Processing order V2: amount=%.2f, payment_intent=%s", paid_amount_doler, intent.get("id"))
            try:
                order = _create_order_from_payment_metadata(
                    metadata,
                    paid_amount_doler,
                    payment_intent_id=intent.get("id")
                )
                logger.info("✨ Order V2 created successfully: order_id=%s", order.id if order else "None")
            except Exception as e:
                logger.warning("Webhook V2 order creation skipped: %s", str(e))
                return Response({"status": "ok"}, status=status.HTTP_400_BAD_REQUEST)


        return Response({"status": "ok"}, status=status.HTTP_200_OK)






from rest_framework import serializers


#order related new work

class CreateOrdersV2(APIView):
    permission_classes = [IsAuthenticated]
    
    def get (self, request):
        pass

    def post(self, request):
        data = request.data
        user = request.user
        logger.info("👤 CreateOrdersV2 endpoint: user=%s, user.id=%s, is_authenticated=%s", user, user.id if hasattr(user, 'id') else 'NO_ID', user.is_authenticated if hasattr(user, 'is_authenticated') else 'N/A')

        serializer = OrderCreateSerializerV2(data=data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": f"{str(next(iter(serializer.errors.values()))[0])}",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product_data = serializer.validated_data.get('product_list')  # [[1,2],[3,4]]

            # Extract product IDs
            product_ids = [item[0] for item in product_data]

            products = Product.objects.filter(id__in=product_ids)
            product_map = {p.id: p for p in products}

            total_amount = 0
            product_names = []
            metadata_products = []

            # ✅ Calculate total properly
            for item in product_data:
                product_id, qty = item

                product = product_map.get(product_id)
                if not product:
                    raise serializers.ValidationError(f"Invalid product id: {product_id}")

                price = product.sale_price if product.sale_price > 0 else product.regular_price

                total_amount += (price + product.tax_price) * qty

                product_names.append(product.product_title)
                metadata_products.append({
                    "product_id": product_id,
                    "qty": qty
                })

            # Address
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
                    "success": False,
                    "message": "validation errors!",
                    "errors": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product_name = ", ".join(product_names)

        
        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),
            currency="gbp",
            description=f"Payment for {product_name}",
            metadata={
                "user_id": str(user.id),
                "products": json.dumps(metadata_products),
                "items": json.dumps(metadata_products),
                "source": "flor_bot_orders",

                # address
                "country_or_region": country_or_region,
                "address_line_i": address_line_i,
                "address_line_ii": address_line_ii,
                "suburb": suburb,
                "city": city,
                "postal_code": postal_code,
                "state": state
            }
        )

        return Response(
            {
                "success": True,
                "payment": {
                    "payment_intent_id": intent.id,
                    "client_secret": intent.client_secret,
                    "amount": total_amount,
                    "currency": "gbp",
                    "product_name": product_name,
                },
                "stripe": {
                    "publishable_key": settings.STRIPE_TEST_PUBLIC_KEY
                }
            },
            status=status.HTTP_200_OK
        )