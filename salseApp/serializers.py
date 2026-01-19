

from rest_framework import serializers
from dashboard.models import Product, Images, Category, OrderTable


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['id', 'image', 'title']
    



class ProductSerializerPublic(serializers.ModelSerializer):
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
            'available_colors',
            'pattern_type',
            'stock_quantity'
            
        ]




class ProductSerializerDetails(serializers.ModelSerializer):
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


class CategorisSerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"



class ProductSerializerDetailsOrder(serializers.ModelSerializer):
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
            'main_category',
            'sub_category',

            'regular_price',
            'sale_price',

            # uploads
            'primary_image',
            'images',
            'uploaded_images',

            # dimensions
            'length',
            'width',
            'thickness',
            'weight',            
        ]

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])

        product = Product.objects.create(**validated_data)

        for image in images_data:
            img_obj = Images.objects.create(image=image)
            product.images.add(img_obj)

        return product
    


class OrderSerializers(serializers.ModelSerializer):
    product = ProductSerializerDetailsOrder()
    
    class Meta:
        model = OrderTable
        fields = [
            'id',
            'product',
            'quantity',
            'order_total',
            'status',

            # fees (optional / admin controlled)
            'delivery_fee',
            'tax_fee',

            # shipping info
            'ship_method',
            'carrier',
            'tracking_no',

            # address
            'country_or_region',
            'address_line_i',
            'address_line_ii',
            'suburb',
            'city',
            'postal_code',
            'state',
        ]

        read_only_fields = [
            'order_total',
        ]

    

from rest_framework import serializers

class OrderCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1)

    delivery_charge = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0
    )
    tax_charge = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0
    )

    # Address
    country_or_region = serializers.CharField(max_length=250)
    address_line_i = serializers.CharField(max_length=250)
    address_line_ii = serializers.CharField(
        max_length=250,
        required=False,
        allow_blank=True
    )
    suburb = serializers.CharField(max_length=250)
    city = serializers.CharField(max_length=250)
    postal_code = serializers.CharField(max_length=50)
    state = serializers.CharField(max_length=250)







class ProductSearchSuggestion(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'product_title',            
            'primary_image'           
        ]

