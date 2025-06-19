from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Agendamento, HealthUnit, Worker 

from .models import Code, HealthUnit, StatusSenha, Worker, TipoSenha, User
from .decorators import worker_required 

@worker_required
def manager_dashboard(request):
    worker = request.user.worker
    health_unit = worker.health_unit

    if not health_unit:
        return HttpResponseBadRequest("Este funcionário não está associado a uma unidade de saúde. Por favor, entre em contato com o administrador.")

    # Senhas aguardando: Prioritárias primeiro, depois normais, as mais antigas primeiro
    waiting_codes = Code.objects.filter(
        health_unit=health_unit,
        status=StatusSenha.AGUARDANDO
    ).order_by('-type_of_code', 'created')

    # Senha em atendimento (se houver)
    in_service_code = Code.objects.filter(
        health_unit=health_unit,
        status=StatusSenha.EM_ATENDIMENTO
    ).first()

    # Senha que está sendo chamada (se houver)
    calling_code = Code.objects.filter(
        health_unit=health_unit,
        status=StatusSenha.CHAMANDO
    ).first()

    # Últimas senhas atendidas
    attended_codes = Code.objects.filter(
        health_unit=health_unit,
        status=StatusSenha.ATENDIDO
    ).order_by('-attended_at')[:5]

    context = {
        'health_unit': health_unit,
        'waiting_codes': waiting_codes,
        'in_service_code': in_service_code,
        'calling_code': calling_code,
        'attended_codes': attended_codes,
        'StatusSenha': StatusSenha, # Passar o choices para o template para uso em formulários
    }
    return render(request, "manager/dashboard.html", context)


@require_POST
@worker_required
def call_next_code(request):
    worker = request.user.worker
    health_unit = worker.health_unit

    if not health_unit:
        return JsonResponse({'error': 'Funcionário não associado a uma unidade de saúde.'}, status=400)

    channel_layer = get_channel_layer()
    room_group_name = f'fila_{health_unit.id}'

    with transaction.atomic():
        # Lógica para "limpar" senhas CHAMANDO ou EM_ATENDIMENTO que não foram concluídas
        # ou marcar como PERDEU a VEZ se uma nova está sendo chamada
        Code.objects.filter(
            health_unit=health_unit,
            status=StatusSenha.CHAMANDO
        ).update(status=StatusSenha.PERDEU) # Ou outro status apropriado

        # Tentar encontrar uma senha prioritária aguardando
        next_code = Code.objects.filter(
            health_unit=health_unit,
            status=StatusSenha.AGUARDANDO,                                              
            type_of_code=TipoSenha.PRIORITARIA
        ).order_by('created').first()

        if not next_code:
            # Se não houver prioritária, tentar encontrar uma normal aguardando
            next_code = Code.objects.filter(
                health_unit=health_unit,
                status=StatusSenha.AGUARDANDO,
                type_of_code=TipoSenha.NORMAL
            ).order_by('created').first()

        if next_code:
            next_code.status = StatusSenha.CHAMANDO
            next_code.called_at = timezone.now()
            next_code.called_by = worker
            next_code.save()

            # Enviar atualização para o grupo via Channels
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'code_updated', # Chama o método code_updated no consumer
                    'message': {
                        'id': next_code.id, # O id do Code é BigAutoField, então é int, não precisa de str()
                        'code_number': next_code.code,
                        'type_of_code': next_code.get_type_of_code_display(),
                        'status': next_code.get_status_display(),
                        'called_at': next_code.called_at.isoformat(),
                        'called_by': worker.user.username,
                        'health_unit_id': str(health_unit.id), # health_unit_id é UUID, então precisa de str()
                        'action': 'called' # Indica que foi uma chamada
                    }
                }
            )
            return JsonResponse({'success': True, 'code_id': next_code.id, 'code_number': next_code.code})
        else:
            return JsonResponse({'error': 'Nenhuma senha para chamar.'}, status=404)


@require_POST
@worker_required
def update_code_status(request, code_id): # Aqui code_id será int
    worker = request.user.worker
    health_unit = worker.health_unit

    if not health_unit:
        return JsonResponse({'error': 'Funcionário não associado a uma unidade de saúde.'}, status=400)

    # Use get_object_or_404 para levantar 404 se a senha não existir ou não pertencer à unidade
    code_instance = get_object_or_404(Code, id=code_id, health_unit=health_unit)
    new_status_raw = request.POST.get('status')

    # Valide o novo status
    if new_status_raw not in [choice[0] for choice in StatusSenha.choices]:
        return JsonResponse({'error': 'Status inválido.'}, status=400)

    new_status = new_status_raw

    channel_layer = get_channel_layer()
    room_group_name = f'fila_{health_unit.id}'

    with transaction.atomic():
        # Lógica para marcar data de atendimento
        if new_status == StatusSenha.ATENDIDO:
            code_instance.attended_at = timezone.now()

        # Lógica para garantir que apenas uma senha por vez esteja "em atendimento" por atendente/unidade, se necessário.
        if new_status == StatusSenha.EM_ATENDIMENTO:
            # Marcar a senha atualmente "EM_ATENDIMENTO" como "CONCLUÍDA" se for diferente
            Code.objects.filter(
                health_unit=health_unit,
                status=StatusSenha.EM_ATENDIMENTO
            ).exclude(id=code_instance.id).update(status=StatusSenha.ATENDIDO, attended_at=timezone.now())

        code_instance.status = new_status
        code_instance.save()

        # Enviar atualização para o grupo via Channels
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'code_updated',
                'message': {
                    'id': code_instance.id, # int, não precisa de str()
                    'code_number': code_instance.code,
                    'type_of_code': code_instance.get_type_of_code_display(),
                    'status': code_instance.get_status_display(),
                    'called_at': code_instance.called_at.isoformat() if code_instance.called_at else None,
                    'attended_at': code_instance.attended_at.isoformat() if code_instance.attended_at else None,
                    'called_by': worker.user.username if code_instance.called_by else None,
                    'health_unit_id': str(health_unit.id),
                    'action': 'status_change'
                }
            }
        )
        return JsonResponse({'success': True, 'new_status': code_instance.get_status_display()})
    

@worker_required
def sched_logs(request):
    worker = request.user.worker
    health_unit = worker.health_unit

    lista_de_agendamentos = Agendamento.objects.filter(
        health_unit=health_unit
    ).select_related('usuario').order_by('-data_agendamento')

    context = {
        'health_unit': health_unit,
        'agendamentos': lista_de_agendamentos,
    }
    
    return render(request, "manager/sched_logs.html", context)