from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from .models import Code, TipoSenha, HealthUnit, StatusSenha
from channels.db import database_sync_to_async 

class CodeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.health_unit_id = self.scope['url_route']['kwargs']['health_unit_id']
        self.room_group_name = f'fila_{self.health_unit_id}' 

        await self.channel_layer.group_add(# Adiciona o canal atual ao grupo específico da unidade
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

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
        # Obtém o próximo número de senha para este tipo DENTRO DESTA UNIDADE
        next_code = await self.get_next_code_for_unit(type_of_code, self.health_unit_id)

        # Cria a instância Code para esta unidade
        created_code = await self.create_code_for_unit(type_of_code, next_code, self.health_unit_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'code_sent',
                'message': {
                    'id': created_code.id,
                    'type_of_code': created_code.get_type_of_code_display(),
                    'code': created_code.code, 
                    'status': created_code.get_status_display(),
                    'created': created_code.created.isoformat(),
                    'health_unit_id': str(self.health_unit_id)
                }
            }
        )


    async def code_sent(self, event):
        await self.send(text_data=json.dumps(event['message']))

    async def code_updated(self, event):
        await self.send(text_data=json.dumps(event['message']))

    async def code_removed(self, event):
        await self.send(text_data=json.dumps(event['message']))

    @sync_to_async
    def get_next_code_for_unit(self, type_of_code, health_unit_id):
        # Filtra por tipo e por unidade de saúde
        last = Code.objects.filter(
            type_of_code=type_of_code,
            health_unit_id=health_unit_id
        ).order_by('-code').first()
        return last.code + 1 if last else 1

    @sync_to_async
    def create_code_for_unit(self, type_of_code, code_number, health_unit_id):
        health_unit = HealthUnit.objects.get(id=health_unit_id)
        return Code.objects.create(
            type_of_code=type_of_code,
            code=code_number,
            health_unit=health_unit, # associa a senha à unidade
            status=StatusSenha.AGUARDANDO #nova senha sempre começa aguardando
        )