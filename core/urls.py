from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "playground"

urlpatterns = [
    path("", TemplateView.as_view(template_name="core/index.html"), name="home"),
]
