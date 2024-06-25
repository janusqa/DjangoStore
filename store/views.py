from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend  # add generic filtering
from rest_framework.filters import SearchFilter  # add searching
from django.db.models.aggregates import Count
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import OrderItem, Product, Collection, Review
from .serializers import (
    CollectionModelSerializer,
    ProductModelSerializer,
    ReviewModelSerializer,
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

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilterSet
    # filterset_fields = ["collection_id"]
    search_fields = ["title", "description", "collection__title"]

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


###
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


###
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
