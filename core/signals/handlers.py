from django.dispatch import receiver
from store.signals import order_created


# handler for a custom reciever
# this subscribes the core app to recieve notifiaions for order_created
# we can also register handlers in any other app that wants to receive  order_created
@receiver(order_created)
def on_order_created(sender, **kwargs):
    print(kwargs["order"])
