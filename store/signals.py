from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Customer


# To register this reciever in store app, in apps.py overrid the ready method
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_for_new_user(sender, **kwargs):
    # kwargs["created"] is a boolean that is True if model was created
    if kwargs["created"]:
        # kwargs["instance"] holds model instance
        Customer.objects.create(user=kwargs["instance"])
