from gc import get_objects

from django.shortcuts import render
from pyexpat.errors import messages
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .serializers import MessageSerializer, MessagePostSerializer
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from asgiref.sync import async_to_sync
from rest_framework_simplejwt.exceptions import TokenError
from chat.models import Message, Room
from chat.serializers import MessageSerializer

# def index(request):
#     return render(request, "chat/index.html")

def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token required."}, status=400)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=205)
        except TokenError:
            return Response({"detail": "Invalid or expired token."}, status=400)


class MessageViewSet(viewsets.GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def history(self, request):
        room_name = request.query_params.get('room_name')
        if not room_name:
            return Response({"detail": "room_name query parameter is required"},status = status.HTTP_400_BAD_REQUEST)
        room = get_object_or_404(Room, name = room_name)

        #check permission
        if not room.is_user_allowed(request.user):
            return Response({"error": "You are not allowed to view this room."}, status = status.HTTP_403_FORBIDDEN)

        messages = Message.objects.filter(room=room).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data[::-1])

    @action(detail=False, methods=['post'])
    def send(self, request):
        room_name = request.data.get('room_name')
        if not room_name:
            return Response({"detail": "room_name query parameter is required"},status = status.HTTP_400_BAD_REQUEST)

        room = get_object_or_404(Room, name =room_name)

        if not room.is_user_allowed(request.user):
            return Response({"error": "You are not allowed to send messages in this room."}, status = status.HTTP_403_FORBIDDEN)

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(user = request.user, room=room)

            channel_layer = get_channel_layer()
            room_group_name = f'chat_{room_name}'

            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'chat.message',
                    'message': message.content,
                    'username': request.user.username,
                    'timestamp': message.timestamp.strftime('%H:%M:%S')

                }
            )
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

