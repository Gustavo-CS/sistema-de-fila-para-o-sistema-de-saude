from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from users_sus.models import User, Code, Worker, Patient, HealthUnit, TipoSenha, StatusSenha, Feedback, Agendamento
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from datetime import datetime

import os

from django.http import HttpResponse, JsonResponse 
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from .forms import FeedbackForm, UNIDADES_SUS_CHOICES

from django.db.models import Count


@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    token = request.POST['credential']

    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
        )
    except ValueError:
        return HttpResponse(status=403)

    email = user_data.get('email')
    if not email:
        return HttpResponse("Email not provided by Google.", status=400)

    try:
        user = User.objects.get(email=email)

        if hasattr(user, 'worker') and user.is_staff:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            request.session['username'] = user.username
            request.session['employee_id'] = str(user.worker.employee_id) 
            return redirect(reverse('manager_dashboard')) 
        
        elif hasattr(user, 'patient'):
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            request.session['username'] = user.username
            request.session['id'] = user.id 
            return redirect("/")
        else:
            return redirect("/register") 

    except User.DoesNotExist:
        return redirect("/register")

    return redirect('/') 

def queue_display_view(request):
    health_unit = get_object_or_404(HealthUnit, id='62d1ca25-e6df-4246-accd-17869aef97f4')

    if not health_unit:
        return render(request, "queue_display.html", {'error': 'Nenhuma unidade de saúde configurada no sistema. Por favor, cadastre uma no painel de administração.'})

    calling_code = Code.objects.filter(
        health_unit=health_unit,
        status=StatusSenha.CHAMANDO
    ).order_by('-called_at').first()

    last_called_or_attended_codes = Code.objects.filter(
        health_unit=health_unit
    ).exclude(status__in=[StatusSenha.AGUARDANDO, StatusSenha.CANCELADO, StatusSenha.PERDEU]).order_by('-called_at', '-attended_at')[:6] # ALTERADO AQUI
    context = {
        'health_unit': health_unit,
        'calling_code': calling_code,
        'last_called_or_attended_codes': last_called_or_attended_codes,
        'next_waiting_code': Code.objects.filter(health_unit=health_unit, status=StatusSenha.AGUARDANDO).order_by('-type_of_code', 'created').first(),
    }
    return render(request, "queue_display.html", context) 

def index(request):
    codes = Code.objects.order_by('-created')[:30]
    return render(request, "index.html", {'codes': codes})


def register_view(request):
    if request.method == 'POST':
        if not request.POST.get('username'):
            return redirect("/register")

        if not request.POST.get('email'):
            return redirect("/register")

        if not request.POST.get('date'):
            return redirect("/register")
        
        if not request.POST.get('address'):
            return redirect("/register")
        
        if not request.POST.get('phone'):
            return redirect("/register")
        
        if len(request.POST.get('phone')) != 11 or not request.POST.get('phone').isdigit():
            return redirect("/register")

        if request.POST.get('password') != request.POST.get('confirmation'):
            return redirect("/register")

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        date = request.POST.get('date')
        phone_number = request.POST.get('phone')
        address = request.POST.get('address')

        user = User(username=username, email=email, birth_date=date)
        user.set_password(password)
        user.save()

        patient = Patient(phone_number=phone_number, address=address, user=user)
        patient.save()
        return redirect("/login")

    return render(request, "register.html")


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            if not hasattr(user, 'patient'):
                return render(request, "login.html", {'error': 'Credenciais inválidas. Verifique seu email e senha.'})
            
            if user.check_password(password):
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.session['username'] = user.username
                request.session['patient_id'] = str(user.patient.patient_id) 
                return redirect("/")
            else:
                return render(request, "login.html", {'error': 'Senha incorreta.'})
        except User.DoesNotExist:
            return render(request, "login.html", {'error': 'Usuário não encontrado.'})
    return render(request, "login.html") 


def login_worker(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)

            if not hasattr(user, 'worker') or not user.is_staff:
                return render(request, "login.html", {'error': 'Credenciais inválidas ou não é um funcionário autorizado.'})

            if user.check_password(password):
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                request.session.save() 

                request.session['username'] = user.username
                request.session['employee_id'] = str(user.worker.employee_id)
                
                return redirect(reverse('manager_dashboard'))

            else:
                return render(request, "login.html", {'error': 'Senha incorreta.'})
        except User.DoesNotExist:
            return render(request, "login.html", {'error': 'Usuário não encontrado.'})
    
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("/")


def create_view(request):
    return render(request, "create.html")


def scheduling_view(request):
    return render(request, "scheduling.html")


def feedback(request):
    unidade_selecionada = request.GET.get('unidade', '')

    todas_unidades = []
    for grupo in UNIDADES_SUS_CHOICES:
        todas_unidades.extend(grupo[1])

    codigos_disponiveis = [codigo for codigo, nome in todas_unidades]

    feedbacks_qs = Feedback.objects.all().order_by('-criado_em')
    if unidade_selecionada and unidade_selecionada != 'todas':
        feedbacks_qs = feedbacks_qs.filter(unidade_sus=unidade_selecionada)

    feedbacks_processados = []
    for fb in feedbacks_qs:
        nome_unidade = next((nome for codigo, nome in todas_unidades if codigo == fb.unidade_sus), fb.unidade_sus)
        feedbacks_processados.append({
            'titulo': fb.titulo,
            'comentario': fb.comentario,
            'criado_em': fb.criado_em,
            'user': fb.user,
            'unidade_nome': nome_unidade,
        })

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            Feedback.objects.create(
                user=request.user,
                unidade_sus=data['unidade_sus'],
                titulo=data['titulo'],
                comentario=data['comentario']
            )
            return redirect('feedback')
    else:
        form = FeedbackForm()

    unidades_para_filtro = [('todas', 'Todas as unidades')] + todas_unidades

    context = {
        'form': form,
        'feedbacks': feedbacks_processados,
        'unidade_selecionada': unidade_selecionada,
        'unidades_para_filtro': unidades_para_filtro,
    }
    return render(request, 'feedback.html', context)

def fila_view(request, numero_senha):
    minha_senha = get_object_or_404(Code, pk=numero_senha)
    senha_atual = get_senha_em_atendimento()

    posicao = Code.objects.filter(
        status='AGU',
        created__lt=minha_senha.created,
        type_of_code=minha_senha.type_of_code
    ).count() + 1

    context = {
        'sua_senha': minha_senha,
        'senha_atual': senha_atual.code if senha_atual else "---",
        'posicao': posicao
    }
    return render(request, 'tela_fila.html', context)

def get_senha_em_atendimento():
    senha_atual = Code.objects.filter(status='ATE').order_by('-created').first()
    return senha_atual

def api_status_fila(request, numero_senha):
    minha_senha = get_object_or_404(Code, pk=numero_senha)
    
    if minha_senha.status != 'AGU':
        posicao = 0
    else:
        posicao = Code.objects.filter(
            status='AGU',
            created__lt=minha_senha.created,
            type_of_code=minha_senha.type_of_code
        ).count() + 1

    senha_atual = get_senha_em_atendimento()

    data = {
        'senha_atual': senha_atual.code if senha_atual else "---",
        'posicao': posicao,
        'seu_status': minha_senha.get_status_display()
    }
    
    return JsonResponse(data)

@login_required
def scheduling_view(request):
    unidades = HealthUnit.objects.all().order_by('name')
    context = {
        'unidades_de_saude': unidades
    }
    return render(request, 'scheduling.html', context) 

@login_required
def salvar_agendamento(request):
    if request.method == 'POST':
        
        unidade_id = request.POST.get('unidade_id')
        especialidade_selecionada = request.POST.get('especialidade')
        data_selecionada = request.POST.get('data_consulta') 
        horario_selecionado = request.POST.get('horario_consulta') 

        data_hora_string = f'{data_selecionada} {horario_selecionado}'
        data_hora_obj = datetime.strptime(data_hora_string, '%Y-%m-%d %H:%M')

        unidade = HealthUnit.objects.get(id=unidade_id)

        Agendamento.objects.create(
            usuario=request.user,
            health_unit=unidade,
            especialidade=especialidade_selecionada,
            data_agendamento=data_hora_obj,
            status='Confirmado'
        )
        
        return redirect('meus_agendamentos')

    return redirect('scheduling')

@login_required
def meus_agendamentos_view(request):
    meus_agendamentos = Agendamento.objects.filter(usuario=request.user).order_by('-data_agendamento')
    context = {
        'agendamentos': meus_agendamentos
    }
    return render(request, 'meus_agendamentos.html', context)

@login_required
def sched_logs_view(request):
    if not hasattr(request.user, 'worker'):
        return redirect('index')

    worker = request.user.worker
    health_unit = worker.health_unit

    if not health_unit:
        return render(request, "sched_logs.html", {'error': 'Você não está associado a uma unidade de saúde.'})

    lista_de_agendamentos = Agendamento.objects.filter(
        health_unit=health_unit
    ).select_related('usuario').order_by('-data_agendamento')

    context = {
        'health_unit': health_unit,
        'agendamentos': lista_de_agendamentos,
    }
    
    return render(request, "sched_logs.html", context)

def search_senhas(request):
    """
    Esta view é chamada pelo JavaScript.
    Ela recebe um termo de busca, filtra as senhas no banco de dados
    e retorna uma lista de senhas em formato JSON.
    """

    term = request.GET.get('term', '')
    
    senha_encontradas = []
    
    
    if len(term) >= 1:
        senhas_qs = Code.objects.filter(code__icontains=term)[:4]
        
        for senha in senhas_qs:
            senha_encontradas.append({
                'id': senha.id,
                'code': senha.code,
                'preferencial': senha.type_of_code,
                'status': senha.status,
            })
            
    return JsonResponse({'senhas': senha_encontradas})
