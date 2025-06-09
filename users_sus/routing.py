from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # (?P<health_unit_id>[0-9a-f-]+) captura um UUID e o passa como argumento nomeado para o consumer
    re_path(r'ws/queue/(?P<health_unit_id>[0-9a-f-]+)/$', consumers.CodeConsumer.as_asgi()),
    re_path(r'ws/codes/$', consumers.CodeConsumer.as_asgi()),
]