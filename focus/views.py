from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib import messages

from django.contrib.auth import views
from focus.forms import LoginForm, SignupForm


class HomeView(TemplateView):
    template_name = 'index.html'


#
# def home(request):
#     return HttpResponse("Hello, world!")


class FormBasicView(TemplateView):
    template_name = 'form.html'


class PasswordChangeView(views.PasswordChangeView):
    success_url = reverse_lazy("focus:password_change_done")


class PasswordResetView(views.PasswordResetView):
    success_url = reverse_lazy("focus:password_reset_done")


class PasswordResetConfirmView(views.PasswordResetConfirmView):
    success_url = reverse_lazy("focus:password_reset_complete")


def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('focus:login')
        else:
            messages.error(request, 'Invalid form data.')
            return redirect('focus:signup')
    form = SignupForm()
    return render(request, 'accounts/page-register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            user_2 = authenticate(request, email=username, password=password)
            if user or user_2:
                login(request, user)
                return redirect('focus:home')
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid form data.')
            return redirect('focus:login')
    form = LoginForm()
    return render(request, 'accounts/page-login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect('focus:login')
