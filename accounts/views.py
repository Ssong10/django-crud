from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm, CustomUserCreationForm
from IPython import embed
from django.contrib.auth import get_user_model

# Create your views here.
def signup(request):
    if request.user.is_authenticated:
        return redirect('articles:index')
    if request.method =="POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('articles:index')
    else: 
        form = CustomUserCreationForm()
    context = {
        'form': form
    }
    return render(request,'accounts/form.html',context)

def login(request):
    if request.method =='POST':
        login_form = AuthenticationForm(request,request.POST)
        if login_form.is_valid():
            user = login_form.get_user()
            auth_login(request, user)
            return redirect(request.GET.get('next') or 'articles:index')
    else:
        login_form = AuthenticationForm()
    context = {
        'login_form' : login_form
    }
    return render(request,'accounts/login.html',context)

def logout(request):
    auth_logout(request)
    return redirect('articles:index')

@login_required
def update(request):
    if request.method =="POST":
        form = CustomUserChangeForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('articles:index')
    else:
        form = CustomUserChangeForm(instance=request.user)
    context = {
        'form': form
    }
    return render(request,'accounts/form.html',context)

@login_required
def password_change(request):
    if request.method =="POST":
        form = PasswordChangeForm(request.user,request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('articles:index')
    else:
        form = PasswordChangeForm(request.user)
    context = {
        'form' : form
    }
    return render(request,'accounts/form.html',context)


def profile(request,account_pk):
    User = get_user_model()
    profile = get_object_or_404(User,pk=account_pk)
    context = {
        'profile':profile,
    }
    return render(request, 'accounts/profile.html',context)

def follow(request,account_pk):
    user = request.user
    User = get_user_model()
    profile = get_object_or_404(User,pk=account_pk)
    if user != profile:
        if profile not in user.followers.all():
            user.followers.add(profile)
        else:
            user.followers.remove(profile)
    context = {
        'profile' :profile
    }
    return render(request,'accounts/profile.html',context)