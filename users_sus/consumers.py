from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from .models import Code, TipoSenha

class CodeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'test'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        type_of_code = data.get('type_of_code', TipoSenha.NORMAL)

        # Get next code number for this type
        next_code = await self.get_next_code(type_of_code)

        # Create Code instance
        created_code = await self.create_code(type_of_code, next_code)

        # Send response to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'code_sent',
                'message': {
                    'id': created_code.id,
                    'type_of_code': created_code.type_of_code,
                    'code': created_code.code,
                    'created': created_code.created.isoformat()
                }
            }
        )

    async def code_sent(self, event):
        await self.send(text_data=json.dumps(event['message']))

    @sync_to_async
    def get_next_code(self, type_of_code):
        last = Code.objects.filter(type_of_code=type_of_code).order_by('-code').first()
        return last.code + 1 if last else 1

    @sync_to_async
    def create_code(self, type_of_code, code_number):
        return Code.objects.create(type_of_code=type_of_code, code=code_number)
