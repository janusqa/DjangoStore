from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import (
    Cart,
    CartItem,
    Customer,
    Order,
    OrderItem,
    Product,
    Collection,
    Review,
)


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
        method_name="get_price_with_tax", read_only=True
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

    def get_price_with_tax(self, product: Product) -> Decimal:
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


class SimpleProductModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["pk", "title", "unit_price"]


class AddCartItemModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["pk", "product_id", "quantity"]

    # note that product_id above is an auto generated at run time so we cannot reference it unless we define it in the serailizer
    product_id = serializers.IntegerField()

    def save(self, **kwargs):
        # We need to override the save method to meet our business requirements which are if a
        # product already exsit in the cart we cannot add it again, instead upsert what is there/
        # recall that in our serializer data is validated and if valid is put in validated_data.
        # in the save method this variable is accessible via self
        product_pk = self.validated_data.get("product_id")
        quantity = self.validated_data.get("quantity")
        cart_pk = self.context["cart_pk"]

        # we need to follow the same cermony as BaseModelSerializer with is parent of ModelSerailzer
        # when overring  its methods. That means we have to set self.instance to our upated or created cart item
        # same as in the save method of the BaseSerializer to ensure all the plumbing is similar. The take away is
        # that you really need to look at the methods you are overriding and try to mimick what they do
        cart_item = CartItem.objects.filter(
            cart__pk=cart_pk, product__pk=product_pk
        ).first()
        if cart_item is not None:
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        else:
            self.instance = CartItem.objects.create(
                cart_id=cart_pk, **self.validated_data
            )

        return self.instance

    # We need to validate the product_id in the save method to prevent us saving a nonexistant product
    # which will throw an exception
    # !!!NOTE!!! this function is specially named so that it is used automatially by django
    # this is a field level validator. It has a pattern of validate_<field_name>
    # When serializer.is_valid is called in a view it will auto invoke any field validators.
    # if the cart_id is invalid that is does not exist in this case an error is raised, else
    # return the field being validated.
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No product with the given ID was found.")
        return value


class UpdateCartItemModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        # note pk is missing because this will be for updates only
        fields = ["quantity"]


class CartItemModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["pk", "product", "quantity", "total_price"]

    product = SimpleProductModelSerializer()
    total_price = serializers.SerializerMethodField("get_total_price")

    def get_total_price(self, cart_item: CartItem) -> Decimal:
        return Decimal(cart_item.quantity) * cart_item.product.unit_price


class CartModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["pk", "item_count", "items", "total_price"]

    # in this case when creating a cart we do not want to send the id
    pk = serializers.UUIDField(read_only=True)
    items = CartItemModelSerializer(
        source="cartitem_set",
        read_only=True,
        many=True,
    )
    item_count = serializers.IntegerField(read_only=True)
    total_price = serializers.SerializerMethodField("get_total_price")

    def get_total_price(self, cart: Cart) -> Decimal:
        return sum(
            [
                Decimal(item.quantity) * item.product.unit_price
                for item in cart.cartitem_set.all()
            ]
        )


class CustomerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "pk",
            "user",
            "phone",
            "birth_date",
            "membership",
        ]

    user = serializers.PrimaryKeyRelatedField(read_only=True)


class OrderItemModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["pk", "product", "unit_price", "quantity"]

    product = SimpleProductModelSerializer()


class CreateOrderModelSerializer(serializers.Serializer):
    # we inherit from regular serializer because what we want to serialzie is not part of the Order Model.
    # i.e cart_id
    cart_id = serializers.UUIDField()

    # this is a field level validator. It has a pattern of validate_<field_name>
    # When serializer.is_valid is called in a view it will auto invoke any field validators.
    # if the cart_id is invalid that is does not exist in this case an error is raised, else
    # return the field being validated.
    def validate_cart_id(self, value):
        if not Cart.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No cart with the given Id was found.")
        if CartItem.objects.filter(cart__pk=value).count() == 0:
            raise serializers.ValidationError("The cart is empty.")
        return value

    # we have specific requirements for saving an order so override save method so must be implemented by hand
    def save(self, **kwargs):
        # make sure to use a transaction so that if any part of updating the db fails we roll back
        # and nothing is done
        with transaction.atomic():
            # 1. Create Order
            customer = Customer.objects.filter(user__pk=self.context["user_id"]).first()
            order = Order.objects.create(customer=customer)

            # 2. Get cart
            # 3. Get items in cart
            cart_items = CartItem.objects.select_related("product").filter(
                cart__pk=self.validated_data["cart_id"]
            )

            # 4. Convert cart Items to Order items
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity,
                )
                for item in cart_items
            ]

            # 5. Save order items to db
            # bulk insert orderitems
            OrderItem.objects.bulk_create(order_items)

            # remove Cart and cart items (deleted by cascade)
            Cart.objects.filter(pk=self.validated_data["cart_id"]).delete()

            return order


class UpdateOrderModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["payment_status"]


class OrderModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["pk", "customer", "placed_at", "payment_status", "orderitem_set"]

    orderitem_set = OrderItemModelSerializer(many=True, read_only=True)


### =================================
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
