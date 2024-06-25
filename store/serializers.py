from decimal import Decimal
from rest_framework import serializers
from store.models import Product, Collection, Review


# !!!NOTE!!! There is a more efficent way of serializing a model. That is to use
# Model serializers


class CollectionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["pk", "title", "product_count"]

    # when creating an object set fields that should not be part of the object as read_only=True
    product_count = serializers.IntegerField(read_only=True)


class ProductModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "pk",
            "title",
            "description",
            "slug",
            "inventory",
            "unit_price",
            "price_with_tax",
            "collection",
            "collection_str",
            "collection_object",
            "collection_str",
            "collection_link",
        ]

    # when creating an object set fields that should not be part of the object as read_only=True
    price_with_tax = serializers.SerializerMethodField(
        method_name="calculate_tax", read_only=True
    )
    # by default the collection included above in meta class gives us by primary key
    collection_str = serializers.StringRelatedField(source="collection", read_only=True)
    collection_object = CollectionModelSerializer(
        source="collection",
        read_only=True,
    )
    collection_link = serializers.HyperlinkedRelatedField(
        source="collection",
        queryset=Collection.objects.all(),
        view_name="store:collections-detail",
    )

    def calculate_tax(self, product: Product) -> Decimal:
        return product.unit_price * Decimal(1.1)

    # customize how a product is created
    # def create(self, validated_data):
    #     product = Product(**validated_data)
    #     # add some new field to product object
    #     product.other = 1
    #     product.save()
    #     return product

    # customize how a product is created
    # instance is a product object
    # def update(self, instance: Product, validated_data):
    #     instance.unit_price = validated_data.get("unit_price")
    #     instance.save()
    #     return instance


class ReviewModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "pk",
            "date",
            "name",
            "description",
            # "product", # No need to this as this will be present as a route parameter in url. This can be read in the ViewSet and passed in the context
            # recall we use a context to pass additional data to a serializer
        ]

    # overwrite the create method for this serializer so set the product_id read from route
    def create(self, validated_data):
        product_pk = self.context["product_pk"]
        return Review.objects.create(product_id=product_pk, **validated_data)


###
### !!!NOTE!!! Every thing below this line is a build up to the model serializers above which replace them
###
### Serializers


class CollectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)


# Generally they are 4 ways to serailize the fields of a model
# 1. Primary Key
# 2. String
# 3. Nested Object
# 4. Hyperlink
class ProductSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    price = serializers.DecimalField(
        source=("unit_price"), max_digits=6, decimal_places=2
    )
    price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax")
    # !!!NOTE!!! below are the various ways to include related field
    # 1. as an id
    # 2. as it's string (__str__) representation
    # 3. as a nested object
    # 4. as a hyperlink to view related object
    collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
    # recall that each model has a __str__ method that represents what it
    # looks like as a string.  That is what is returned by StringRelatedField
    collection_str = serializers.StringRelatedField(source="collection")
    collection_object = CollectionSerializer(source="collection")
    collection_link = serializers.HyperlinkedRelatedField(
        source="collection",
        queryset=Collection.objects.all(),
        view_name="store:collection_detail",
    )

    def calculate_tax(self, product: Product) -> Decimal:
        return product.unit_price * Decimal(1.1)
