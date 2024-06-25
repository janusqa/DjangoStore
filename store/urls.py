from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

app_name = "store"

router = SimpleRouter()
router.register("products", viewset=views.ProductViewSet, basename="proudcts")
router.register("collections", viewset=views.CollectionViewSet, basename="collections")

urlpatterns = [
    path("", include(router.urls)),
    # path("products/", views.product_list, name="products"),
    # path("products/", views.ProductListCreate.as_view(), name="products"),
    # path("products/<int:pk>/", views.product_detail, name="product_detail"),
    # path(
    #     "products/<int:pk>/",
    #     views.ProductDetailRetrieveUpdateDestroy.as_view(),
    #     name="product_detail",
    # ),
    # path("collections/", views.collection_list, name="collections"),
    # path("collections/", views.CollectionListCreate.as_view(), name="collections"),
    # path("collections/<int:pk>/", views.collection_detail, name="collection_detail"),
    # path(
    #     "collections/<int:pk>/",
    #     views.CollectionDetailRetrieveUpdateDestroy.as_view(),
    #     name="collection_detail",
    # ),
]
