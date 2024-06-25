from django_filters.rest_framework import FilterSet

from store.models import Product


class ProductFilterSet(FilterSet):
    class Meta:
        model = Product

        # order matters in how filters will be listed in the dict and the arrays
        fields = {
            "collection_id": ["exact"],
            "unit_price": ["gt", "lt"],
        }
