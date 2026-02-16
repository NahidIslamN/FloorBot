"""
Serializers for AI App API
"""
from rest_framework import serializers
from dashboard.models import Product, Images, Category


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['id', 'image', 'title']


class TextMessageSerializer(serializers.Serializer):
    """Serializer for text message input"""
    message = serializers.CharField(required=True, max_length=2000)
    session_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class VoiceMessageSerializer(serializers.Serializer):
    """Serializer for voice message input (base64 format)"""
    audio_data = serializers.CharField(required=True, help_text="Base64 encoded audio")
    audio_format = serializers.ChoiceField(
        choices=['wav', 'mp3', 'webm', 'm4a', 'ogg'],
        default='wav'
    )
    session_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    language = serializers.CharField(default='en', max_length=10)


class VoiceFileSerializer(serializers.Serializer):
    """Serializer for voice file upload (multipart/form-data)"""
    audio_file = serializers.FileField(required=True, help_text="Audio file from microphone")
    session_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    language = serializers.CharField(default='en', max_length=10)


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product data - uses ModelSerializer to match backend"""
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
            'stock_quantity',
            'return_policy'
            
        ]


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat response output"""
    session_id = serializers.CharField()
    response = serializers.CharField()
    success = serializers.BooleanField()
    error = serializers.CharField(required=False, allow_null=True)
    transcribed_text = serializers.CharField(required=False, allow_null=True)
    products = ProductSerializer(many=True, required=False, allow_null=True)
    product_count = serializers.IntegerField(required=False, allow_null=True)


class SessionSerializer(serializers.Serializer):
    """Serializer for session information"""
    session_id = serializers.CharField()
    user_id = serializers.CharField(required=False, allow_null=True)
    created_at = serializers.DateTimeField()


class ConversationHistorySerializer(serializers.Serializer):
    """Serializer for conversation history"""
    session_id = serializers.CharField()
    messages = serializers.ListField()
    success = serializers.BooleanField()
    message = serializers.CharField(required=False, allow_null=True)


class SessionRequestSerializer(serializers.Serializer):
    """Serializer for session ID in request"""
    session_id = serializers.CharField(required=True)
