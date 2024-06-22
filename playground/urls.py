from django.urls import path
from . import views

app_name = "playground"

urlpatterns = [
    path("hello/", views.say_hello, name="hello"),
    path("hello1/", views.say_hello1, name="hello1"),
    path("hello2/", views.say_hello2, name="hello2"),
    path("hello3/", views.say_hello3, name="hello3"),
]
