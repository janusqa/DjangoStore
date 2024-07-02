from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.db.models import UniqueConstraint
from django.conf import settings
from uuid import uuid4

from store.validators import validate_file_size


# Create your models here.
class Customer(models.Model):
    MEMBERSHIP_BRONZE = "B"
    MEMBERSHIP_SILVER = "S"
    MEMBERSHIP_GOLD = "G"

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, "Bronze"),
        (MEMBERSHIP_SILVER, "Silver"),
        (MEMBERSHIP_GOLD, "Gold"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # email = models.EmailField(unique=True) # already in user model
    # first_name = models.CharField(max_length=255) # already in user model
    # last_name = models.CharField(max_length=255) # already in user model
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE
    )

    def __str__(self) -> str:
        return f"{self.user.last_name}, {self.user.first_name}"

    class Meta:
        ordering = ["user__last_name", "user__first_name"]
        permissions = [("view_history", "Can view history")]


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip = models.CharField(max_length=255, null=True)
    # customer = models.OneToOneField(
    #     Customer, on_delete=models.CASCADE, primary_key=True
    # ) # one-to-one relationship
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # one-to-many

    def __str__(self) -> str:
        return f"{self.street} | {self.city} | {self.zip} ({self.customer.email})"


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()

    def __str__(self) -> str:
        return f"{self.description}"


# 1. Name clashes: use related_name='+' to tell django we want to buy pass creating the reverse
# relationship, as it already exists from previous work. This will prevent
# name clashes. You can also use realated_name to give relation a diffent name too
# to avoid clashing with an existing name.
# 2. Circular dependancy where Collection has a relationship with Product and
# Product has relationship with Collection. We solve this by putting for instanmce
# Proudct in quotations. That resolves the dependance where product has to be
# declared before Collection.
class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        "Product", on_delete=models.SET_NULL, null=True, related_name="+"
    )

    def __str__(self) -> str:
        return f"{self.title}"

    class Meta:
        ordering = ["title"]


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal(1), message="Ensure this value is greater than or equal to 1."
            )
        ],
    )
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(
        Promotion, blank=True
    )  # blank ensures that this field is optional

    def __str__(self) -> str:
        return f"{self.title}"

    class Meta:
        ordering = ["title"]


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="store/images", validators=[validate_file_size])
    # image = models.FileField(
    #     upload_to="store/images",
    #     validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    # )

    def __str__(self) -> str:
        return f"{self.image}"


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Cart: {self.pk}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        # set a unique constraint such that comaination of cart + product is a unique key in across cartitem table
        # i.e a specific cart can only contain a product once.
        constraints = [
            UniqueConstraint(fields=["cart", "product"], name="unique_cart_product")
        ]

    def __str__(self) -> str:
        return f"Cart:{self.cart.pk} -> {self.pk}"


class Order(models.Model):
    PAYMENT_STATUS_PENDING = "P"
    PAYMENT_STATUS_COMPLETE = "C"
    PAYMENT_STATUS_FAILED = "F"

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, "Pending"),
        (PAYMENT_STATUS_COMPLETE, "Complete"),
        (PAYMENT_STATUS_FAILED, "Failed"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING
    )
    placed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Order:{self.pk}, Customer: {self.customer.user.email}"

    class Meta:
        # creates a custom permission to cancel an order
        permissions = [("cancel_order", "Can cancel order")]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self) -> str:
        return f"Order:{self.order.pk} -> {self.pk}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Review:{self.pk} -> Product: {self.product.title}"
