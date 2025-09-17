from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages


class CustomLoginView(LoginView):
    """Custom login view with template and redirect handling"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            # Automatically log in the user after registration
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'There was an error with your registration.')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def home_view(request):
    """Simple home view to test authentication"""
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')