from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, default="Admin")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','password']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        related_query_name='custom_user',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        related_query_name='custom_user',
        blank=True,
    )

    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'User'


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    date = models.DateField()
    total_tickets = models.IntegerField()
    ticket_sold = models.IntegerField(default=0)

    class Meta:
        db_table = 'Event'


class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Ticket'

