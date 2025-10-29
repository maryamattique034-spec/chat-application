from django.db import models

# Create your models here.
class Message(models.Model):
    room_name = models.CharField(max_length=200)
    user =  models.CharField(max_length=100, default='anonymous')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.user}: {self.message[:20]}"

class Room(models.Model):
    name = models.CharField(max_length=100, unique = True)

    def __str__(self):
        return self.name