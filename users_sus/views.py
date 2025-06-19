from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from users_sus.models import User, Code, Worker, Patient, HealthUnit, TipoSenha, StatusSenha, Feedback
from django.urls import reverse
from django.views.decorators.http import require_GET

import os

from django.http import HttpResponse, JsonResponse 
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from .forms import FeedbackForm
from .choices import UNIDADES_POR_ESTADO

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

        #lógica para redirecionar funcionários para o painel de gestão
        if hasattr(user, 'worker') and user.is_staff: # verifica se o usuário é um worker e tem is_staff=True
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            request.session['username'] = user.username
            request.session['employee_id'] = str(user.worker.employee_id) 
            return redirect(reverse('manager_dashboard')) 
        
        #lógica para login de paciente (se não for worker)
        elif hasattr(user, 'patient'):
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            request.session['username'] = user.username
            request.session['id'] = user.id 
            return redirect("/")
        else:
            #caso o usuário exista, mas não seja nem paciente nem funcionário
            return redirect("/register") 

    except User.DoesNotExist:
        #se não existe, vai para registro
        return redirect("/register")

    return redirect('/') 

def queue_display_view(request):
    # UUID DA UNIDADE DE SAÚDE 
    health_unit = get_object_or_404(HealthUnit, id='62d1ca25-e6df-4246-accd-17869aef97f4')

    if not health_unit:
        return render(request, "queue_display.html", {'error': 'Nenhuma unidade de saúde configurada no sistema. Por favor, cadastre uma no painel de administração.'})

    calling_code = Code.objects.filter(
        health_unit=health_unit,
        status=StatusSenha.CHAMANDO
    ).order_by('-called_at').first()

    last_called_or_attended_codes = Code.objects.filter(
        health_unit=health_unit
    ).exclude(status__in=[StatusSenha.AGUARDANDO, StatusSenha.CANCELADO, StatusSenha.PERDEU]).order_by('-called_at', '-attended_at')[:10]

    context = {
        'health_unit': health_unit,
        'calling_code': calling_code,
        'last_called_or_attended_codes': last_called_or_attended_codes,
        'next_waiting_code': Code.objects.filter(health_unit=health_unit, status=StatusSenha.AGUARDANDO).order_by('-type_of_code', 'created').first(),
    }
    return render(request, "queue_display.html", context) 



# Create your views here.
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
            #verifica se o usuário é um Patient
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
    print("--- Tentativa de Login de Funcionário ---")
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        print(f"Email recebido: {email}")
        
        try:
            user = User.objects.get(email=email)
            print(f"Usuário encontrado: {user.email}")
            print(f"Usuário é staff: {user.is_staff}")
            print(f"Usuário tem worker associado: {hasattr(user, 'worker')}")

            if not hasattr(user, 'worker') or not user.is_staff:
                print("ERRO: Usuário não é um worker ou não é staff.")
                return render(request, "login.html", {'error': 'Credenciais inválidas ou não é um funcionário autorizado.'})

            # Se o usuário é um Worker, tenta fazer o login
            if user.check_password(password):
                print("Senha CORRETA. Logando e redirecionando.")
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                request.session.save() 
                print("Sessão salva.") 

                request.session['username'] = user.username
                request.session['employee_id'] = str(user.worker.employee_id)
                
                return redirect(reverse('manager_dashboard'))

            else:
                print("ERRO: Senha INCORRETA.")
                return render(request, "login.html", {'error': 'Senha incorreta.'})
        except User.DoesNotExist:
            print("ERRO: Usuário NÃO ENCONTRADO com este email.")
            return render(request, "login.html", {'error': 'Usuário não encontrado.'})
    
    print("Requisição GET ou não POST. Renderizando formulário.")
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("/")


def create_view(request):
    return render(request, "create.html")


def scheduling_view(request):
    return render(request, "scheduling.html")

def feedback(request):
    estado_selecionado = request.GET.get('estado', '')
    unidade_selecionada = request.GET.get('unidade', '')

    feedbacks_qs = Feedback.objects.none()

    if estado_selecionado:
        unidades_do_estado = [codigo for codigo, nome in UNIDADES_POR_ESTADO.get(estado_selecionado, [])]

        if unidade_selecionada and unidade_selecionada != 'todas':
            feedbacks_qs = Feedback.objects.filter(unidade_sus=unidade_selecionada).order_by('-criado_em')
        else:
            feedbacks_qs = Feedback.objects.filter(unidade_sus__in=unidades_do_estado).order_by('-criado_em')


    feedbacks_processados = []
    for fb in feedbacks_qs:
        nome_unidade = None
        for unidades in UNIDADES_POR_ESTADO.values():
            for codigo, nome in unidades:
                if codigo == fb.unidade_sus:
                    nome_unidade = nome
        feedbacks_processados.append({
            'titulo': fb.titulo,
            'comentario': fb.comentario,
            'criado_em': fb.criado_em,
            'user': fb.user,
            'unidade_nome': nome_unidade or fb.unidade_sus,
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

    estados_choices = [(sigla, sigla) for sigla in UNIDADES_POR_ESTADO.keys()]
    unidades_do_estado = UNIDADES_POR_ESTADO.get(estado_selecionado, [])

    unidades_para_filtro = [('todas', 'Todas as unidades')] + unidades_do_estado

    context = {
        'form': form,
        'feedbacks': feedbacks_processados,
        'estado_selecionado': estado_selecionado,
        'unidade_selecionada': unidade_selecionada,
        'estados_choices': estados_choices,
        'unidades_para_filtro': unidades_para_filtro,
    }
    return render(request, 'feedback.html', context)


@require_GET
def unidades_por_estado_view(request):
    estado = request.GET.get('estado')
    unidades = UNIDADES_POR_ESTADO.get(estado, [])
    return JsonResponse(unidades, safe=False)

def fila_view(request, numero_senha):
    """Renderiza a página inicial com os dados da fila."""
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
    """Busca a última senha chamada que está 'EM_ATENDIMENTO'."""
    senha_atual = Code.objects.filter(status='ATE').order_by('-created').first()
    return senha_atual

def api_status_fila(request, numero_senha):
    """Fornece dados atualizados da fila para o frontend."""
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
