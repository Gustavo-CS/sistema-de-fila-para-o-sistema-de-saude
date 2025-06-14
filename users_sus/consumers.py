from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from .models import Code, TipoSenha, HealthUnit, StatusSenha
from channels.db import database_sync_to_async

class CodeConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.health_unit_id = self.scope['url_route']['kwargs']['health_unit_id']
        self.room_group_name = f'fila_{self.health_unit_id}'
        print(f"CONSUMER: Conectando à unidade específica: {self.health_unit_id}")

        try:
            await database_sync_to_async(HealthUnit.objects.get)(id=self.health_unit_id)
        except HealthUnit.DoesNotExist:
            print(f"CONSUMER: Unidade de saúde com ID {self.health_unit_id} não encontrada. Fechando conexão.")
            await self.close() # Fecha a conexão se a unidade não existir
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print("CONSUMER: Conexão WebSocket aceita.")

    async def disconnect(self, close_code):
        print(f"CONSUMER: Desconectando do grupo {self.room_group_name}.")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"CONSUMER: Mensagem recebida: {text_data}")
        data = json.loads(text_data)
        type_of_code = data.get('type_of_code', TipoSenha.NORMAL)
        
        # health_unit_id agora sempre virá de self.health_unit_id
        next_code_number = await self.get_next_code_for_unit(type_of_code, self.health_unit_id) 
        created_code = await self.create_code_for_unit(type_of_code, next_code_number, self.health_unit_id)

        print(f"CONSUMER: Senha criada: {created_code.code} tipo {created_code.type_of_code}")

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
                    'health_unit_id': str(self.health_unit_id) # health_unit_id é UUID, precisa de str()
                }
            }
        )
        print("CONSUMER: Mensagem enviada para o grupo.")

    async def code_sent(self, event):
        print(f"CONSUMER: Enviando mensagem 'code_sent' para o cliente: {event['message']}")
        await self.send(text_data=json.dumps(event['message']))

    async def code_updated(self, event):
        print(f"CONSUMER: Enviando mensagem 'code_updated' para o cliente: {event['message']}")
        await self.send(text_data=json.dumps(event['message']))

    async def code_removed(self, event):
        print(f"CONSUMER: Enviando mensagem 'code_removed' para o cliente: {event['message']}")
        await self.send(text_data=json.dumps(event['message']))

    @sync_to_async
    def get_next_code_for_unit(self, type_of_code, health_unit_id): 
        last = Code.objects.filter(
            type_of_code=type_of_code,
            health_unit_id=health_unit_id # Agora sempre filtra pelo ID da unidade
        ).order_by('-code').first()
        return last.code + 1 if last else 1

    @sync_to_async
    def create_code_for_unit(self, type_of_code, code_number, health_unit_id):
        health_unit = HealthUnit.objects.get(id=health_unit_id) 
        return Code.objects.create(
            type_of_code=type_of_code,
            code=code_number,
            health_unit=health_unit, 
            status=StatusSenha.AGUARDANDO
        )