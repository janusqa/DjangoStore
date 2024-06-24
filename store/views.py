from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Collection
from .serializers import CollectionModelSerializer, ProductModelSerializer


# Create your views here.
@api_view(["GET", "POST"])
def product_list(request) -> Response:
    if request.method == "GET":
        products_queryset = Product.objects.select_related("collection").all()
        serializer = ProductModelSerializer(
            products_queryset, many=True, context={"request": request}
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


@api_view(["GET", "PUT"])
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

    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view()
def collection_detail(request, pk: int) -> Response:

    collection = Collection.objects.filter(pk=pk).first()
    if collection is not None:
        serializer = CollectionModelSerializer(collection, context={"request": request})

        # serializer contains attribute called data which contains
        # the product converted to a dictionary for us.
        # When we pass this dict to Response Django/Rest_Framework
        # under the hood will convert it to json before sending
        return Response(serializer.data)

    return Response(status=status.HTTP_404_NOT_FOUND)
