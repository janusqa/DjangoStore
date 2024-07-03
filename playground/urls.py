from django.urls import path
from . import views

app_name = "playground"

urlpatterns = [
    path("hello/", views.say_hello, name="hello"),
    path("hello1/", views.say_hello1, name="hello1"),
    path("hello2/", views.say_hello2, name="hello2"),
    path("hello3/", views.say_hello3, name="hello3"),
    path("hello4/", views.say_hello4, name="hello4"),
    path("hello5/", views.say_hello5, name="hello5"),
    path("hello6/", views.say_hello6, name="hello6"),
    path("hello7/", views.say_hello7, name="hello7"),
    path("hello8/", views.say_hello8, name="hello8"),
    path("hello9/", views.say_hello9, name="hello9"),
]
