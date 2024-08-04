import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator


# Set the Django settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jerry_project.settings')

# Ensure Django is set up before importing models or components
django.setup()

from django.core.asgi import get_asgi_application
from jerry_project.router import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
