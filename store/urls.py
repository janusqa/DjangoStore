from django.urls import path, include
from rest_framework_nested import routers
from . import views

app_name = "store"

router = routers.DefaultRouter()
router.register("products", viewset=views.ProductViewSet, basename="proudcts")
router.register("collections", viewset=views.CollectionViewSet, basename="collections")
router.register("carts", viewset=views.CartViewSet, basename="carts")

# lookup is the prefix for the route parmeter we will be looking for eg. product_pk
# eg. https://localhost/products/product_pk/reviews/1
products_router = routers.NestedDefaultRouter(router, "products", lookup="product")
products_router.register(
    "reviews", viewset=views.ReviewViewSet, basename="product-reviews"
)

# lookup is the prefix for the route parmeter we will be looking for
# eg. https://localhost/carts/cart_pk/reviews/1
carts_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
carts_router.register("items", viewset=views.CartItemViewSet, basename="cart-items")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(products_router.urls)),
    path("", include(carts_router.urls)),
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
