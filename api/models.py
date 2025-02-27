from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)  # Admin flag

class TravelRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=255)
    purpose_travel = models.TextField()
    travel_start_date = models.DateField()
    travel_mode = models.CharField(max_length=100)
    ticket_booking_mode = models.CharField(max_length=100)
    travel_start_loc = models.CharField(max_length=255)
    travel_end_loc = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.project_name}"


