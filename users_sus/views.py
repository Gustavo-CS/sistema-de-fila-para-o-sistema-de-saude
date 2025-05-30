from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from users_sus.models import User, Code, Worker, Patient

import os

from django.http import HttpResponse
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

        username = user.username
        id = user.id

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        request.session['username'] = username
        request.session['id'] = id
        return redirect("/")

    except User.DoesNotExist:
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

        print(username, email, password, date)
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
            try:
                patient = Patient.objects.get(user=user)
                id = str(patient.patient_id)
                username = user.username
                if user.check_password(password):
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    request.session['username'] = username
                    request.session['patient_id'] = id
                    return redirect("/")
            except Patient.DoesNotExist:
                return render(request, "login.html")
        except User.DoesNotExist:
            print("No user found with that email.")
    return render(request, "login.html")


def login_worker(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            try:
                worker = Worker.objects.get(user=user)
                id = str(worker.employee_id)
                username = user.username
                if user.check_password(password):
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    request.session['username'] = username
                    request.session['employee_id'] = id
                    return redirect("/")
            except Worker.DoesNotExist:
                return render(request, "login.html")
        except User.DoesNotExist:
            print("No worker found with that email.")
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("/")


def create_view(request):
    return render(request, "create.html")


def scheduling_view(request):
    return render(request, "scheduling.html")