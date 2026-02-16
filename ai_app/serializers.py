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

    # Accept either a related model instance or a primitive PK in responses.
    # Some code paths provide product data as dicts (e.g. from the chatbot),
    # so use a SerializerMethodField to safely return the PK when needed.
    main_category = serializers.SerializerMethodField()
    
    # Handle primary_image URL properly
    primary_image = serializers.SerializerMethodField()

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

    def get_main_category(self, obj):
        # obj may be a model instance, a dict, or an int PK
        try:
            # model instance with attribute
            if hasattr(obj, 'main_category'):
                mc = obj.main_category
                return mc.pk if mc is not None else None

            # dict-like representation
            if isinstance(obj, dict):
                return obj.get('main_category')

            # fallback if obj itself is an int
            if isinstance(obj, int):
                return obj

        except Exception:
            return None
    
    def get_primary_image(self, obj):
        """Get the URL for primary_image"""
        try:
            # Handle model instance with FileField/ImageField
            if hasattr(obj, 'primary_image'):
                primary = getattr(obj, 'primary_image')
                if primary:
                    # Preferred: direct URL from storage
                    try:
                        url = getattr(primary, 'url', None)
                        if url:
                            return url
                    except Exception:
                        # storage may raise when file missing; fall through to name/path fallback
                        pass

                    # Fallback: use file name/path and MEDIA_URL if available
                    name = getattr(primary, 'name', None) or str(primary)
                    if name:
                        try:
                            from django.conf import settings
                            media_url = getattr(settings, 'MEDIA_URL', '') or ''
                            if media_url:
                                return media_url.rstrip('/') + '/' + name.lstrip('/')
                            return name
                        except Exception:
                            return name

            # Handle dict-like representations coming from chatbot/service
            if isinstance(obj, dict):
                val = obj.get('primary_image')
                if not val:
                    return None

                # If it's already a full URL, return it
                if isinstance(val, str) and (val.startswith('http://') or val.startswith('https://')):
                    return val

                # If it's a path/name, try MEDIA_URL fallback
                try:
                    from django.conf import settings
                    media_url = getattr(settings, 'MEDIA_URL', '') or ''
                    if media_url and isinstance(val, str):
                        return media_url.rstrip('/') + '/' + str(val).lstrip('/')
                except Exception:
                    pass

                return val

        except Exception:
            return None

        return None



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
