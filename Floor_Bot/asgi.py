import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Floor_Bot.settings')
django.setup()

# Import routing AFTER django.setup()
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from chat_app.routing import websocket_urlpatterns
from .custom_auth import CustomAuthMiddleware

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            CustomAuthMiddleware(
                URLRouter(
                    websocket_urlpatterns
                )
            )
        )
    }
)
