from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import EmployeeProfile, CustomerProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'EMPLOYEE':
            EmployeeProfile.objects.get_or_create(user=instance)
        elif instance.role == 'CUSTOMER':
            CustomerProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'EMPLOYEE' and hasattr(instance, 'employee_profile'):
        instance.employee_profile.save()
    elif instance.role == 'CUSTOMER' and hasattr(instance, 'customer_profile'):
        instance.customer_profile.save()