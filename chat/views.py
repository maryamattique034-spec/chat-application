from django.shortcuts import render, redirect, get_object_or_404
from .models import Message, Room
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

# def room(request,room_name,):
#     return render(request, 'chat/room.html',{
#         'room_name': room_name
#     })


def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'chat/room-list.html', {'rooms': rooms})

@login_required(login_url = 'login')
def room(request,room_name,):
    room = get_object_or_404(Room,name = room_name)
    messages = Message.objects.filter(room_name=room_name).order_by('timestamp')
    return render(request, 'chat/room.html',{
        'room_name': room_name,
        'messages': messages
    })

def user_login(request):
    if request.user.is_authenticated:
        return redirect('room-list')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username , password=password)
        if user is not None:
            login(request,user)
            return redirect('room-list')
        else:
            logout(request)
            messages.error(request, 'Invalid username or password')
    return render(request, 'chat/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')