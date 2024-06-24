from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("products/", views.product_list, name="products"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("collections/<int:pk>/", views.collection_detail, name="collection_detail"),
]
