from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


def home(request):
    # TODO: implement home/welcome page
    return render(request, 'zoo_app/home.html')


def user_login(request):
    # TODO: implement login logic
    return render(request, 'zoo_app/login.html')


def register(request):
    # TODO: implement registration logic
    return render(request, 'zoo_app/register.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('zoo_app:home')


@login_required
def dashboard(request):
    # TODO: implement dashboard with study stats
    return render(request, 'zoo_app/dashboard.html')


@login_required
def zoo(request):
    # TODO: implement zoo page showing user's animals
    return render(request, 'zoo_app/zoo.html')


@login_required
def shop(request):
    # TODO: implement animal shop
    return render(request, 'zoo_app/shop.html')


@login_required
def study_hub(request):
    # TODO: implement study hub with tasks and timer
    return render(request, 'zoo_app/study_hub.html')


@login_required
def notes(request):
    # TODO: implement notes and resources page
    return render(request, 'zoo_app/notes.html')
