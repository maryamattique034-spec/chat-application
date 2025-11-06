from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    user1= models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_user1')
    user2= models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_user2')

    def __str__(self):
        return f"{self.user1.username} & {self.user2.username}"

    def is_user_allowed(self, user):
        print("Checking access for:", user)
        print("Room users:", self.user1, self.user2)
        print("Comparison results:", user == self.user1, user == self.user2)
        #check if the given user is one of two participants.
        return user == self.user1 or user == self.user2

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.user.username}:{self.content[:20]}'