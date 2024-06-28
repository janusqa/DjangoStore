from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend  # add generic filtering
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)  # add searching, ordering
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import permissions

from .permissions import IsAdminOrReadOnly

from .pagination import DefaultPagePagination
from .models import Cart, CartItem, Customer, OrderItem, Product, Collection, Review
from .serializers import (
    AddCartItemModelSerializer,
    CartItemModelSerializer,
    CartModelSerializer,
    CollectionModelSerializer,
    CustomerModelSerializer,
    ProductModelSerializer,
    ReviewModelSerializer,
    UpdateCartItemModelSerializer,
)
from .filters import ProductFilterSet


# Create your views here.


### Genercic ViewSets
# Note that for scenarios where our ViewSet should only List or retrive a single object we have "ReadOnlyModelViewSet"
class ProductViewSet(ModelViewSet):
    # add generic filtering, no need to manually set up filtering for each param we want to filter by
    ## for more info https://django-filter.readthedocs.io/en/stable
    ## We will do a more complex filter on unit_price where we want to filter by a range
    ## 1. create filters.py in store app
    ## 2. set up Filterset classes derived from FilterSet, and define your filtering there
    ## 3. replace filterset_fields with filterset_class

    # add searching by adding SearchFilter to filter_backends, and set up search_fields=[] to the fields we want to search by
    # add ordering by adding OrderingFilter to filter_backends, and set up ordering_fields=[] to the fields we want to search by

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilterSet
    # filterset_fields = ["collection_id"]
    search_fields = ["title", "description", "collection__title"]
    ordering_fields = ["unit_price", "last_update", "collection__pk"]
    permission_classes = [
        IsAdminOrReadOnly,
    ]

    # add pagination (this is page pagination, we can also have limit and offset pagination, see pagination.py)
    ## 1. create pagination.py in store app and set up Pagination classes as needed that you can cusomize. They will be derived from PageNumberPagination
    pagination_class = DefaultPagePagination

    def get_queryset(self):
        return Product.objects.select_related("collection").all()

        ## !!!NOTE!!! Old way of maunally setting up filtering we now use generic filtering above
        # query_set = Product.objects.select_related("collection").all()
        ## apply a filter by collection if we have a collection_id query param in the query string
        ## we can read query params via self.request.query_params just like we can read route params via self.kwargs
        ## !!!NOTE!!! we have to use .get method as collection_id may not exist in query_params and we do not want to
        ## throw and uneccesary error. If it does not exist the .get method will return None
        # collection_id = self.request.query_params.get("collection_id")
        # if collection_id is not None:
        #     query_set = query_set.filter(collection__pk=collection_id)
        # return query_set

    def get_serializer_class(self):
        return ProductModelSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    # we overried the delecte function as we needed to do custom logic not available in the default delete
    # here we are checking that no orders are attached to ths product before deleting
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product__pk=kwargs["pk"]).count > 0:
            return Response(
                {
                    "error": "Product cannot be deleted, because it is associated with an order item"
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    permission_classes = [
        IsAdminOrReadOnly,
    ]

    def get_queryset(self):
        return Collection.objects.annotate(product_count=Count("product"))

    def get_serializer_class(self):
        return CollectionModelSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection__pk=kwargs["pk"]).count > 0:
            return Response(
                {
                    "error": "Collection cannot be deleted, because it is associated with a product"
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    def get_queryset(self):
        # recall that self.kwargs contains the route params
        return Review.objects.select_related("product").filter(
            product__pk=self.kwargs["product_pk"]
        )

    def get_serializer_class(self):
        return ReviewModelSerializer

    def get_serializer_context(self):
        # Access route parameters via kwargs, get the product id from it and pass it to the serializer via context
        # recall we use a context to pass additional data to a serializer
        return {"request": self.request, "product_pk": self.kwargs["product_pk"]}


# !!!NOTE!!! We do not need update or list operations, only create, retrieve and delete. So we need to customized this ViewSet
# we only inherit from the classes we need that ModelViewSet itself inherits from
class CartViewSet(
    CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    def get_queryset(self):
        # "cartitem_set". What this does is preload each cartitem using "cartitem_set",
        # and for each item preload its related product with "__product". This is new knowledge
        return Cart.objects.prefetch_related("cartitem_set__product").annotate(
            item_count=Count("cartitem")
        )

    def get_serializer_class(self):
        return CartModelSerializer

    def get_serializer_context(self):
        return {"request": self.request}


class CartItemViewSet(ModelViewSet):
    # constrain the methods that this ViewSet will service
    #!!!NOTE!!! the array value of methods is CASE-SENSITIVE. MUST BE LOWERCASE
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        # recall that self.kwargs contains the route params
        return CartItem.objects.select_related("product").filter(
            cart__pk=self.kwargs["cart_pk"]
        )

    # customize this to return a serializer based on method
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemModelSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemModelSerializer
        return CartItemModelSerializer

    def get_serializer_context(self):
        # Access route parameters via kwargs, get the product id from it and pass it to the serializer via context
        # recall we use a context to pass additional data to a serializer
        return {"request": self.request, "cart_pk": self.kwargs["cart_pk"]}


# originally we wante to only allow create, update, retrieve from endpoint (Admin UI can list and delete)
# now lets make this more consistent by allow all methods, but restrict CRUD to admin users only, BUT
# allow /me to be accessible to authenticated users. that is we mus apply permissions class AdminOrReadOnly
# to this class but for /me action override with IsAuthenticated
# class CustomerViewSet(
#     CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
# ):
class CustomerViewSet(ModelViewSet):
    # Permissions: !!!NOTE!!! this is defined as a list where we can put multiple permission classes. If any of them fail
    # the client will not be able to access this view
    # IsAdminUser is used here instead of IsAdminOrReadOnly because we dont want ANY METHOD at all to be accessible unless
    # you are authenticated AND an admin user.
    # permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Customer.objects.select_related("user").all()

    def get_serializer_class(self):
        return CustomerModelSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    # lets say we have a very custom business rule that requires different permission for
    # create (CreateModelMixin) and retrieve (RetrieveModelMixin) and update (UpdatedModelMixin). We then have to override
    # "get_permission" method. For example a user can retrieve without authentication but must be authenticated to update.
    # def get_permissions(self):
    #     if self.request.method in permissions.SAFE_METHODS:
    #         # !!!NOTE!!! returning a list of permission objects eg "AllowAny()"" with parens,
    #         # unlike "permission_classes" where we just specify the class
    #         return [AllowAny()]
    #     return [IsAuthenticated()]

    # business logic has change to allow put and get on /me for authenticated users and any other action requires admin user
    def get_permissions(self):
        if self.action == "me":
            # !!!NOTE!!! returning a list of permission objects eg "AllowAny()"" with parens,
            # unlike "permission_classes" where we just specify the class
            return [IsAuthenticated()]
        return [IsAdminUser()]

    # detail=False means this action is accessible from list view i.e. localhost:8000/store/customer/me
    # detail=True means this action is accessible from detail view i.e. localhost:8000/store/customer/1/me

    # @action(detail=False, methods=["GET", "PUT"], permission_classes=[IsAuthenticated])  # can also overrid permission per action
    @action(detail=False, methods=["GET", "PUT"])
    def me(self, request):
        # every request has an attribute user if user is logged in, other whise it is set to AnonymousUser class
        customer = Customer.objects.filter(user__pk=request.user.pk).first()
        if request.method == "GET":
            serializer = CustomerModelSerializer(customer)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = CustomerModelSerializer(customer, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


### =================================
### !!!NOTE!!! Every thing below this line is a build up to the generic class viewsets above which replace them
###
### Generic Class Views
#### GenericView Types
###### CreateAPIView
###### ListAPIView
###### RetrieveAPIView
###### DestoryAPIView
###### UpdateAPIView
###### ListCreateAPIView
###### RetrieveUpdateAPIView
###### RetrieveDestroyAPIView
###### RetrieveUpdateDestroyAPIView
###
class ProductListCreate(ListCreateAPIView):
    def get_queryset(self):
        return Product.objects.select_related("collection").all()

    def get_serializer_class(self):
        return ProductModelSerializer

    def get_serializer_context(self):
        return {"request": self.request}


# Customized Generic View
class ProductDetailRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Product.objects.select_related("collection").all()

    def get_serializer_class(self):
        return ProductModelSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    # we overried the delecte function as we needed to do custom logic not available in the default delete
    # here we are checking that no orders are attached to ths product before deleting
    def delete(self, request, pk: int) -> Response:
        product = Product.objects.filter(pk=pk).first()
        if product is not None:
            # check that product is not in any active orders. if it is do not delete, send appropriate error
            if product.orderitem_set.count() > 0:
                return Response(
                    {
                        "error": "Product cannot be deleted, because it is associated with an order item"
                    },
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_404_NOT_FOUND)


class CollectionListCreate(ListCreateAPIView):
    def get_queryset(self):
        return Collection.objects.annotate(product_count=Count("product"))

    def get_serializer_class(self):
        return CollectionModelSerializer

    def get_serializer_context(self):
        return {"request": self.request}


class CollectionDetailRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Collection.objects.annotate(product_count=Count("product"))

    def get_serializer_class(self):
        return CollectionModelSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def delete(self, request, pk: int) -> Response:
        collection = (
            Collection.objects.annotate(product_count=Count("product"))
            .filter(pk=pk)
            .first()
        )
        if collection is not None:
            # check that product is not in any active orders. if it is do not delete, send appropriate error
            if collection.product_set.count() > 0:
                return Response(
                    {
                        "error": "Collection cannot be deleted, because it is associated with a product"
                    },
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )
            collection.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_404_NOT_FOUND)


### =================================
### !!!NOTE!!! Every thing below this line is a build up to the generic class views above which replace them
###
### Class Views
class ProductList(APIView):
    def get(self, request) -> Response:
        queryset = Product.objects.select_related("collection").all()
        serializer = ProductModelSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request) -> Response:
        # deserialize AND validate the request body
        serializer = ProductModelSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            # print(serializer.validated_data)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetail(APIView):
    def get(self, request, pk: int) -> Response:
        product = Product.objects.filter(pk=pk).first()
        if product is not None:
            serializer = ProductModelSerializer(product, context={"request": request})
            # serializer contains attribute called data which contains
            # the product converted to a dictionary for us.
            # When we pass this dict to Response Django/Rest_Framework
            # under the hood will convert it to json before sending
            return Response(serializer.data)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk: int) -> Response:
        product = Product.objects.filter(pk=pk).first()
        if product is not None:
            serializer = ProductModelSerializer(
                product, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                # print(serializer.validated_data)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk: int) -> Response:
        product = Product.objects.filter(pk=pk).first()
        if product is not None:
            # check that product is not in any active orders. if it is do not delete, send appropriate error
            if product.orderitem_set.count() > 0:
                return Response(
                    {
                        "error": "Product cannot be deleted, because it is associated with an order item"
                    },
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_404_NOT_FOUND)


###
### !!!NOTE!!! Every thing below this line is a build up to the class  views above which replace them
###
###
### Function Views
@api_view(["GET", "POST"])
def product_list(request) -> Response:
    if request.method == "GET":
        queryset = Product.objects.select_related("collection").all()
        serializer = ProductModelSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)
    elif request.method == "POST":
        # deserialize AND validate the request body
        serializer = ProductModelSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            # print(serializer.validated_data)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def product_detail(request, pk: int) -> Response:
    product = Product.objects.filter(pk=pk).first()
    if product is not None:
        if request.method == "GET":
            serializer = ProductModelSerializer(product, context={"request": request})
            # serializer contains attribute called data which contains
            # the product converted to a dictionary for us.
            # When we pass this dict to Response Django/Rest_Framework
            # under the hood will convert it to json before sending
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = ProductModelSerializer(
                product, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                # print(serializer.validated_data)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == "DELETE":
            # check that product is not in any active orders. if it is do not delete, send appropriate error
            if product.orderitem_set.count() > 0:
                return Response(
                    {
                        "error": "Product cannot be deleted, because it is associated with an order item"
                    },
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET", "POST"])
def collection_list(request):
    if request.method == "GET":
        queryset = Collection.objects.annotate(product_count=Count("product"))
        serializer = CollectionModelSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)
    elif request.method == "POST":
        # deserialize AND validate the request body
        serializer = CollectionModelSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            # print(serializer.validated_data)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def collection_detail(request, pk: int) -> Response:

    collection = (
        Collection.objects.annotate(product_count=Count("product"))
        .filter(pk=pk)
        .first()
    )
    if collection is not None:
        if request.method == "GET":
            serializer = CollectionModelSerializer(
                collection, context={"request": request}
            )

            # serializer contains attribute called data which contains
            # the product converted to a dictionary for us.
            # When we pass this dict to Response Django/Rest_Framework
            # under the hood will convert it to json before sending
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = CollectionModelSerializer(
                collection, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                # print(serializer.validated_data)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == "DELETE":
            # check that product is not in any active orders. if it is do not delete, send appropriate error
            if collection.product_set.count() > 0:
                return Response(
                    {
                        "error": "Collection cannot be deleted, because it is associated with a product"
                    },
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )
            collection.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_404_NOT_FOUND)
