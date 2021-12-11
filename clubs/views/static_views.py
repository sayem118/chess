from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from clubs.helpers import login_prohibited

@login_prohibited
def home(request):
    return render(request, 'home.html')

@login_required
def start(request):
    return render(request, 'start.html')
