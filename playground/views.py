from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, mail_admins, BadHeaderError, EmailMessage
from django.db.models.aggregates import Count, Max, Min, Avg


# @required when you want to use OR in your queries,
# F required when you want to compare db fields against each other
from django.db.models import Q, F, Value, Func, ExpressionWrapper
from django.db.models.functions import Concat
from django.db.models import DecimalField
from django.db import transaction, connection
from django.contrib.contenttypes.models import ContentType

from templated_mail.mail import BaseEmailMessage

from store.models import Collection, Product, OrderItem, Order, Customer
from tags.models import Tag, TaggedItem


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

    # use a lookup type eg. "contains". Other lookup types are "startswith" etc
    query_set = Product.objects.filter(title__contains="coffee")

    query_set = Product.objects.filter(last_update__year=2021)  # extract parts of data

    query_set = Product.objects.filter(description__isnull=True)

    query_set = Product.objects.filter(inventory__lt=10, unit_price__lt=20)
    query_set = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20)

    # Use Q objects to implement filtering with OR. The bitwise or is the OR
    query_set = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20))

    # we can still do AND, but the friendlier way is to past multple kewords as in above
    query_set = Product.objects.filter(Q(inventory__lt=10) & Q(unit_price__lt=20))

    # negation to produce NOT in sequel
    query_set = Product.objects.filter(Q(inventory__lt=10) & ~Q(unit_price__lt=20))

    # Referencing fields using F objects
    # eg find products where inventory = price
    query_set = Product.objects.filter(inventory=F("unit_price"))
    query_set = Product.objects.filter(inventory=F("collection__id"))

    # Ordering
    query_set = Product.objects.order_by("title")
    query_set = Product.objects.order_by("-title")  # descending order
    query_set = Product.objects.order_by("unit_price", "-title")
    product = Product.objects.order_by("unit_price")[0]

    # limiting
    query_set = Product.objects.all()[:5]  # get first 5 objects.
    query_set = Product.objects.all()[5:10]  # get next 5 objects.

    # for product in query_set:
    #     print(product)

    return render(request, "playground/hello.html", {"products": list(query_set)})


def say_hello1(request):
    # select only certain fields in query_set
    query_set = Product.objects.values("id", "title", "collection__title")

    query_set = Product.objects.values("id", "title", "collection__title")

    query_set = Product.objects.filter(
        pk__in=OrderItem.objects.values("product__id").distinct()
    ).order_by("title")

    # deferring fields using "only". This is different from using "values"
    # "only" is different from "values" becuase "values" return a dictionary of
    # objects while with "only" we get actual instances of the object returned
    query_set = Product.objects.only("id", "title")
    # !!!NOTE!!! values do not exhibit the same issues as "only" and "defer"

    # deferring fields using "only". This is different from using "values"
    # "only" is different from "values" becuase "values" return a dictionary of
    # objects while with "only" we get actual instances of the object returned
    # !!!NOTE!!!. In your template trying to access a field not mentioned in
    # the query below will send as many queries to the db as they are products.
    # so in the template if you say "{{ product.unit_price }}" to display unit_price
    # and thery are 1000 proudcts, 1000 queries, one per product, will be sent to
    # db to get the unit price
    query_set = Product.objects.only("id", "title")

    # To mitigate the above issue of inefficient query handling we can use the
    # "defer" method, which is opposite of "only" method, as shown below. With "defer"
    # we can defer the loading of certain fields until later. Sw with query below
    # we can access safely any field in template.  BUT AGAIN if we then try to access
    # "description" field we will have same issue as "only" where many queires
    # will be sent to db.
    query_set = Product.objects.defer("description")

    return render(request, "playground/hello.html", {"products": list(query_set)})


def say_hello2(request):
    # Filling related fields for an object using
    # 1. "select_related"
    # 2. "prefetch_related"

    # !!!NOTE!!! in template we are displaying prduct title, product.collection.id
    # Using query belwo we will run int to inefficient query handling again like
    # we did with "only" and "defer".
    # !!!NOTE!!! these problems occur when trying to display a value in the template
    # not easisly accessibly by the underlying base query so other queries have to
    # be performed on top of it. Below we djanto will ONLY query the products table
    # initally, it will not query related tables at all. Querying related table
    # in this instance will happen when we then try to access such inforamation
    # in the template.
    query_set = Product.objects.all()

    # !!!NOTE!!! The good news is we can specifically instruct django to to prefetch
    # related information with base query to avoid the issue of then having to do
    # it per product/object when accessing related information and sending a ton of
    # queries to do so using "select_related" method.
    query_set = Product.objects.select_related("collection").all()

    # !!!NOTE!!!  We use "selected_related" if the main object we are querying on
    # only has one to one relationship with related field. Eg. Product only
    # is in one collection.
    # There is another method called "prefetch_related". This is used when the
    # the related field is one-to-many or many-to-meny. Eg one product can have
    # many promotions. To preloaded the promotions
    query_set = Product.objects.prefetch_related("promotions").all()

    # !!!NOTE!!! we can combine these. The order of which you chain them does
    # not matter either
    query_set = (
        Product.objects.prefetch_related("promotions")
        .select_related("collection")
        .all()
    )

    # fetch last 5 orders with related customer and product information
    # Recall that the reverse relation of orderitem in the order table
    # by convention is called "orderitem_set" NOT "orderitem" or "orderitem_id"
    # etc. We could use "related_name" keyword to rename the relation in
    # the order table but best pratice is to go with django convention
    # !!!NOTE!!! in case below we are spanning orderitem and loading
    # it's related field product
    query_set = (
        Order.objects.select_related("customer")
        .prefetch_related("orderitem_set__product")
        .order_by("-placed_at")[:5]
    )

    # Aggregates
    result = Product.objects.aggregate(Count("pk"))
    result = Product.objects.aggregate(count=Count("pk"))
    result = Product.objects.aggregate(count=Count("pk"), min_price=Min("unit_price"))
    result = Product.objects.filter(collection__id=4).aggregate(
        count=Count("pk"), min_price=Min("unit_price")
    )

    # Annotations
    # Add additional information to an object while querying it
    # must use an Expression object based on the Expression class
    # some Expression objects are
    # 1. Value : for represting boolean, numbers and strings,
    # 3. F : for referencing fields,
    # 3. Func : for calling database functions,
    # 4. Aggregate : base class for all aggregate classes like SUM etc
    # 5. ExpressionWrapper: for building complex expressions

    # add dynamically generated is_new boolean field to customer objects returned by query
    customers = list(Customer.objects.annotate(is_new=Value(True)))

    # give customers a dynamically generated new_id field
    customers = list(Customer.objects.annotate(new_id=F("id")))

    # can perform coumputations
    customers = list(Customer.objects.annotate(new_id=F("id") + 1))

    # Database functions
    # CONCAT function
    customers = list(
        Customer.objects.annotate(
            full_name=Func(
                F("first_name"), Value(" "), F("last_name"), function="CONCAT"
            )
        )
    )

    # Django provides us alternative way to directly call DB functions.
    # We just need to import them and replace the general Func with the
    # function in question. See example below.
    # code is shorter, cleaner with exact same result
    # A clearn use of CONCAT
    customers = list(
        Customer.objects.annotate(
            full_name=Concat("first_name", Value(" "), "last_name")
        )
    )

    # view number of orders per customer
    # usually we would use "order_set" but due to the great geniues at Django
    # we must break tradition and for God knows what reason use "order". If
    # we use "order_set" an exception will be thrown and we can see in it
    # the list of fields we have acess too. Which is how we discovered we
    # should use "order"
    customers = list(Customer.objects.annotate(num_orders=Count("order")))

    # ExpressionWrappers
    discounted_price = ExpressionWrapper(
        F("unit_price") * 0.8, output_field=DecimalField()
    )
    query_set = Product.objects.annotate(discounted_price=discounted_price)

    return render(request, "playground/hello.html", {"result": result})


def say_hello3(request):

    # querying by generic types (tags, likes)
    # 1. find contenttype_id of the object we are interested in
    # 2. use that in conjuction with the object_id to find what we are interested in

    # returns row in content_type table that represents the object, in this case Product
    contenty_type = ContentType.objects.get_for_model(Product)

    query_set = TaggedItem.objects.select_related("tag").filter(
        content_type=contenty_type,
        object_id=1,
    )

    # Custom Query Manager to encapsulate the above code to make querying easier
    query_set = TaggedItem.objects.get_tags_for(Product, 5)

    return render(request, "playground/hello.html", {"objects": list(query_set)})


def say_hello4(request):
    # Creating an object and saving it to the db
    collection = Collection()
    collection.title = "Video Games"

    # 2 ways to set a related/foreign key field
    collection.featured_product = Product(pk=1)
    collection.featured_product__id = 1

    # Above we set fields individually, but we can create the object using it's
    # constructor
    collection = Collection(title="Video Games", featured_product=Product(pk=1))

    # save to db
    collection.save()
    print(collection.id)

    return render(request, "playground/hello.html", {"name": "JanusQA"})


def say_hello5(request):
    # Updating an object and saving it to the db
    collection = Collection.objects.filter(pk=11).first()

    if collection is not None:
        collection.title = "Games"
        collection.featured_product = None
        collection.save()

    # Updating just some fields in an object and saving it to the db
    collection = Collection.objects.filter(pk=11).first()
    if collection is not None:
        collection.featured_product = None
        collection.save()

    # Deleting objects

    # Deleting a single object
    collection = Collection.objects.filter(pk=11).first()
    if collection is not None:
        collection.delete()

    query_set = Collection.objects.filter(pk__gt=11)
    if query_set is not None:
        query_set.delete()

    return render(request, "playground/hello.html", {"name": "JanusQA"})


def say_hello6(request):
    # Transactions

    with transaction.atomic():
        order = Order()
        order.customer = Customer(pk=1)
        order.save()

        item = OrderItem()
        item.order = order
        item.product = Product(pk=1)
        item.quantity = 1
        item.unit_price = 10
        item.save()

    return render(request, "playground/hello.html", {"name": "JanusQA"})


def say_hello7(request):
    # Raw SQL

    query_set = Product.objects.raw("SELECT * FROM store_product")

    # other fields are deferred so be careful accessing them
    query_set = Product.objects.raw("SELECT id, title FROM store_product")

    # by pass using the model
    with connection.cursor() as cursor:
        cursor.execute("SELECT title FROM store_product")

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                title 
            FROM 
                store_product
            WHERE
                id = %s 
            AND 
                unit_price < %s
        """,
            [1, 10],
        )

    return render(
        request,
        "playground/hello.html",
        {"name": "JanusQA", "objects": list(query_set)},
    )


def say_hello8(request):
    try:
        send_mail("subject", "message", "admin@home.test", ["bob@home.test"])
        mail_admins(
            "subject", "message", html_message="message"
        )  # mailing admins #set up site admins in settings.py using "ADMINS"

        # create a message and attach a file
        message = EmailMessage(
            "subject", "message", "admin@home.test", ["john@home.test"]
        )
        message.attach_file("playground/static/images/dog.jpg")
        message.send()

        # create a mail from template
        message1 = BaseEmailMessage(
            template_name="playground/email_hello.html",
            context={"name": "JanusQA"},  # send variables to template
        )
        message1.send(["john@home.text"])
    except BadHeaderError:
        pass  # return some error to client
    return render(
        request,
        "playground/hello.html",
        {"name": "JanusQA"},
    )
