from django.shortcuts import render, redirect
from .models import Message
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

# def room(request,room_name,):
#     return render(request, 'chat/room.html',{
#         'room_name': room_name
#     })

@login_required(login_url = 'login')
def room(request,room_name,):
    messages = Message.objects.filter(room_name=room_name).order_by('timestamp')
    return render(request, 'chat/room.html',{
        'room_name': room_name,
        'messages': messages
    })

def user_login(request):
    if request.user.is_authenticated:
        return redirect('room', room_name= 'general')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username , password=password)
        if user is not None:
            login(request,user)
            return redirect('room', room_name = 'general')
        else:
            logout(request)
            messages.error(request, 'Invalid username or password')
    return render(request, 'chat/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')