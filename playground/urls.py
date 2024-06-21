from django.urls import path
from . import views

app_name = "playground"

urlpatterns = [
    path("hello/", views.say_hello, name="hello"),
]
