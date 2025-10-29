from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_list, name = 'room-list'),
    path('login/', views.user_login, name = 'login'),
    path('logout/', views.user_logout, name = 'logout'),
    path('<str:room_name>/', views.room, name='room'),

]
