from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from users_sus.models import User

# Create your views here.
def index(request):
    return render(request, "index.html")

def register_view(request):
    if request.method == 'POST':
        if not request.POST.get('username'):
            return redirect("/register")

        if not request.POST.get('email'):
            return redirect("/register")

        if not request.POST.get('date'):
            return redirect("/register")

        if request.POST.get('password') != request.POST.get('confirmation'):
            return redirect("/register")

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        date =request.POST.get('date')

        print(username, email, password, date)
        user = User(username=username, email=email, birth_date=date)
        user.set_password(password)
        user.save()
        return redirect("/login")




    return render(request, "register.html")

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.get(email=email)
        username = user.username
        id = user.id
        if user.check_password(password):
            login(request, user)
            request.session['username'] = username
            request.session['id'] = id
            return redirect("/")
        else:
            print(user)
            print('Email ou senha inválidos')
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("/")