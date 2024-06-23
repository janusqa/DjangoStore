from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem


# the relation between product and tag is a generic one so we use
# a differt tabularinline called "GenericTabularInline"
class TagInline(GenericTabularInline):
    model = TaggedItem
    autocomplete_fields = ["tag"]


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline]


# Register your models here.
admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
