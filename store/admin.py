from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.db.models.aggregates import Count
from django.utils.html import format_html  # implement links for list in admin ui
from django.utils.http import urlencode  # implement links for list in admin ui
from django.urls import reverse  # implement links for list in admin ui
from . import models


# This is a custom filter. To enable it add it to list_filters list
class InventoryFilter(admin.SimpleListFilter):
    title = "inventory level"  # appers after By in title
    parameter_name = "inventory"  # what will appear in querystring to filter by

    # what we can filter by eg. filter by title, filter by last 7 days etc.
    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        # return list of tuples of the lookups ('expression of filter', 'human readable label')
        return [
            ("<10", "Low"),
        ]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


class ProductAdmin(admin.ModelAdmin):
    actions = ["clear_inventory"]
    ## BEGIN FORM MODIFICATION EXAMPLES
    # fields =['title', 'slug'] # choose fields to show on form
    # exclude= ['promotions'] # choose fields to hid on form
    # read_only =['title'] # make the title a read only field
    prepopulated_fields = {
        "slug": ["title"],
    }
    # auto complete fields are useful for dropdowns that may have a large number
    # of items. We do not want to overload the ui like that, so use auto-complet
    # fields. !!!NOTE!!! we mush add all autocomplete fields also as search fields
    # in for the object we want to seach in. In this example that is "collection",
    # so add 'title' as a search field in CollectionAdmin
    autocomplete_fields = ["collection"]
    ## END FORM MODIFICATION EXAMPLES
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
    list_filter = ["collection", "last_update", InventoryFilter]

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

    # this is a custom action for the admin product list. to activate
    # add it to the actions list for this Admin Manager
    # queryset is the items in the list that are selected by the user
    @admin.action(description="clear inventory for selected items")
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        # the below "message_user" is a admin feature that allows sending
        # messages to logged in user
        self.message_user(
            request,
            f"{updated_count} products were successfully updated.",
            messages.SUCCESS,
        )


class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership", "orders_count"]
    list_editable = ["membership"]
    ordering = ["first_name", "last_name"]
    list_per_page = 10
    # search_fields = ["first_name", "last_name"]
    # embelllish search fields with lookup type "startwith"
    search_fields = ["first_name__startswith", "last_name__startswith"]

    @admin.display(ordering="orders_count")
    def orders_count(self, customer):
        url_string = reverse("admin:store_order_changelist")
        query_string = urlencode({"customer__pk": customer.pk})
        return format_html(
            f"<a href='{url_string}?{query_string}'>{customer.orders_count}</a>"
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(orders_count=Count("order"))


class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ["customer"]
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
    search_fields = ["title"]
    list_display = ["title", "products_count"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        # return collection.products_count
        #!!!NOTE!!! how to link a related column to its list page
        # get the link to the related admin list we use "reverse"
        # reverse('admin:ourAppName_targetModel_targetPage')
        url_string = reverse("admin:store_product_changelist")
        # filter the related list via a querystring
        query_string = urlencode({"collection__pk": collection.pk})
        # combine both into final url and return the resultant formatted url
        url = f"{url_string}?{query_string}"  # page is called "changelist"
        return format_html(f"<a href='{url}'>{collection.products_count}</a>")

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
