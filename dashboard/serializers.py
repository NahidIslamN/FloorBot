from rest_framework import serializers
from .models import Product, Images, Category, OrderTable


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['id', 'image', 'title']


class ProductSerializer(serializers.ModelSerializer):
    # accept multiple image files
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    # show images in response
    uploaded_images = ImageSerializer(
        source='images',
        many=True,
        read_only=True
    )

    main_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'product_title',
            'brand_manufacturer',
            'item_description',
            'main_category',
            'sub_category',

            # uploads
            'primary_image',
            'images',
            'uploaded_images',

            # pricing
            'regular_price',
            'sale_price',
            'product_id',
            'pack_coverage',

            # dimensions
            'length',
            'width',
            'thickness',
            'weight',
            'installation_method',
            'coverage_per_pack',

            # categorized details
            'pile_height',
            'materials',
            'format',
            'is_underlay_required',
            'is_calculate',
            'available_colors',
            'pattern_type',
            'stock_quantity'
        ]

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])

        product = Product.objects.create(**validated_data)

        for image in images_data:
            img_obj = Images.objects.create(image=image)
            product.images.add(img_obj)

        return product

from auths.models import CustomUser

class UserData(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "full_name",
            "image",
        ]

class CustoerFeedBack(serializers.ModelSerializer):
    user = UserData()
    class Meta:
        model = OrderTable
        fields = [
            'user',
            'custormer_feedback',
        ]



class OrderTableSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = OrderTable
        fields = [
            "quantity",
            "ship_method",
            "status",
            "carrier",
            "tracking_no",
            "is_shiped",
        ]



class CustomerDataSerialziser(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "full_name",
            "email",
            "phone",
            "image"

        ]


class OrderedProduct(serializers.ModelSerializer):
    # accept multiple image files
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    # show images in response
    uploaded_images = ImageSerializer(
        source='images',
        many=True,
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'product_title',
            'item_description',
            'primary_image',
            'images',
            'uploaded_images',
            # pricing
            'regular_price',
            'sale_price',
            'product_id',
            'is_calculate',
        ]


class OrderTableSerializerView(serializers.ModelSerializer):
    user = CustomerDataSerialziser()
    product = OrderedProduct()
    class Meta:
        model = OrderTable
        fields = [
            "user",
            "product",
            "quantity",
            "delivery_fee",
            "tax_fee",
            "order_total",
            "ship_method",
            "status",
            "carrier",
            "tracking_no",
            "is_paid",
            "is_shiped",
            "country_or_region",
            "address_line_i",
            "address_line_ii",
            "suburb",
            "city",
            "postal_code",
            "state",
            "custormer_feedback",
            "is_feedbacked",
        ]