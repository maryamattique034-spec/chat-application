from rest_framework import serializers
from chat.models import Message


class MessageSerializer(serializers.ModelSerializer):
    # Display the username instead of the user ID
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'room', 'username', 'content', 'timestamp']
        read_only_fields = ['user', 'room']  # User and room will be set in the View


class MessagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content']  # Only content is sent in the POST request