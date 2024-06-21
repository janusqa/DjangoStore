from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product


# Create your views here.
def say_hello(request):
    query_set = Product.objects.all()

    try:
        product = Product.objects.get(pk=4)  # throws exception
    except ObjectDoesNotExist:
        pass

    product = Product.objects.filter(
        pk=4
    ).first()  # does not throw exception if product not found

    product_exists = Product.objects.filter(pk=4).exists()

    query_set = Product.objects.filter(unit_price__gt=20)

    query_set = Product.objects.filter(unit_price__range=(20, 30))

    query_set = Product.objects.filter(
        collection__id__range=(1, 3)
    )  # span over attributes of foreign key

    query_set = Product.objects.filter(title__contains="coffee")

    query_set = Product.objects.filter(last_update__year=2021)  # extract parts of data

    query_set = Product.objects.filter(description__isnull=True)

    # for product in query_set:
    #     print(product)

    return render(request, "playground/hello.html", {"products": list(query_set)})
