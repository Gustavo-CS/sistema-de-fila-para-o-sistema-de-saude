from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from .models import Code, TipoSenha

class CodeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        type_of_code = data.get('type_of_code', TipoSenha.NORMAL)

        # Get next code number for this type
        next_code = await self.get_next_code(type_of_code)

        # Create Code instance
        created_code = await self.create_code(type_of_code, next_code)

        # Send response back
        await self.send(text_data=json.dumps({
            'id': created_code.id,
            'type_of_code': created_code.type_of_code,
            'code': created_code.code,
            'created': created_code.created.isoformat()
        }))

    @sync_to_async
    def get_next_code(self, type_of_code):
        last = Code.objects.filter(type_of_code=type_of_code).order_by('-code').first()
        return last.code + 1 if last else 1

    @sync_to_async
    def create_code(self, type_of_code, code_number):
        return Code.objects.create(type_of_code=type_of_code, code=code_number)