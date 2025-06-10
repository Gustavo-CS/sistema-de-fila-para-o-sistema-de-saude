from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from users_sus.models import User, Code, Worker, Patient, HealthUnit, TipoSenha, StatusSenha
from django.urls import reverse 

import os

from django.http import HttpResponse, JsonResponse 
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests



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