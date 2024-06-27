from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.admin import UserAdmin
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem
from .models import AppUser


# Configure our new user for Admin console
# Register it below
class UserCustomAdmin(UserAdmin):
    # we got this from the UserAdmin code. It's how we set what fields appear in admin iterface
    # when adding a new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


# the relation between product and tag is a generic one so we use
# a differt tabularinline called "GenericTabularInline"
class TagInline(GenericTabularInline):
    model = TaggedItem
    autocomplete_fields = ["tag"]


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline]


# Register your models here.
admin.site.register(AppUser, UserCustomAdmin)
admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
