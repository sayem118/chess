from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from .models import User
from .forms import LogInForm, SignUpForm
from django.urls import reverse
from .helpers import login_prohibited
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next = request.POST.get('next') or 'start'
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                redirect_url = next or 'start'
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    else:
        next = request.GET.get('next') or 'start'
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form, 'next': next})

@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('start')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

@login_prohibited
def home(request):
    logout(request)
    return render(request, 'home.html')

def log_out(request):
    logout(request)
    return redirect('home')

@login_required
def start(request):
    return render(request, 'start.html')
