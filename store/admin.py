from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.db.models.aggregates import Count
from . import models


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "unit_price",
        "inventory_status",
        "collection",
        "collection_title",
    ]  # configure what columns we want to display
    list_editable = ["unit_price"]  # make a field in list directly editable
    list_per_page = 10  # change the default pagination
    list_select_related = [
        "collection"
    ]  # prefetch collection info to avoid too many queries

    # use decorator to configure things like how this computed column should be sorted
    @admin.display(ordering="inventory")
    def inventory_status(self, product: models.Product):
        if product.inventory < 10:
            return "Low"
        return "OK"

    # displays a particular field of related object. We cannot use our usual
    # collection__title here so we need to do it via method
    def collection_title(self, product: models.Product):
        return product.collection.title


class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership"]
    list_editable = ["membership"]
    ordering = ["first_name", "last_name"]
    list_per_page = 10


class OrderAdmin(admin.ModelAdmin):
    list_display = ["pk", "placed_at", "customer", "customer_email"]
    ordering = ["placed_at"]
    list_per_page = 10
    list_select_related = ["customer"]

    def customer_email(self, order: models.Order):
        return order.customer.email


# we want to display product count in list, but no products_count field in collection
# so we must override the basquery for this list using (get_queryset) then we can use
# it. This is example of overridng the base query for a list in the admin UI
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "products_count"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        return collection.products_count

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count=Count("product"))


# Register your models here.
admin.site.register(models.Customer, CustomerAdmin)
admin.site.register(models.Address)
admin.site.register(models.Promotion)
admin.site.register(models.Collection, CollectionAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Cart)
admin.site.register(models.CartItem)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.OrderItem)
