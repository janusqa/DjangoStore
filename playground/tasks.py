from time import sleep


from celery import shared_task


@shared_task
def notify_customers(message):
    print("Sending10 emails...")
    print(message)
    sleep(10)  # using sleep for 10s to mock a long running task
    print("Emails were successfully sent!")
