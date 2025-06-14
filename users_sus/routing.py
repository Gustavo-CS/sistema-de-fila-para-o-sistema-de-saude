from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/queue/(?P<health_unit_id>[0-9a-f-]+)/$', consumers.CodeConsumer.as_asgi()),
]