from django.db import models
from oauth2_provider.models import AbstractApplication
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from eth_account import Account
from django.conf import settings

class CustomUser(AbstractUser):
    ethereum_address = models.CharField(max_length=42, blank=False, null=True)  # Ethereum address field
    
    # Add related_name to avoid conflict with the default User model fields
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='customuser'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser'
    )

class MyApplication(AbstractApplication):
    pass

# models.py
class MedicalHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    condition = models.CharField(max_length=255)
    treatment = models.CharField(max_length=255)
    record_id = models.IntegerField(null=True, blank=True)
    date_diagnosed = models.DateField()
    notes = models.TextField(blank=True)


    def __str__(self):
        return f"{self.condition} - {self.user.username}"

class Prescription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    medication_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    prescribed_date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.medication_name} prescribed to {self.user.username}"
