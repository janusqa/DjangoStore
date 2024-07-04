from locust import HttpUser, task, between
from random import randint


class WebsiteUser(HttpUser):

    wait_time = between(
        1, 5
    )  # locust will wait randomly 1, 5 seconds between each task

    # the higer the task weight the more likely it is to happen
    # !!!NOTE!!! a task can be weightless.  that is just be "@task"
    # Viewing products
    @task(2)  # task with a weight of 2
    def view_products(self):
        collection_pk = randint(2, 6)
        self.client.get(
            f"/store/products?collection_pk={collection_pk}", name="/store/products"
        )

    # Viewoing product details
    @task  # task with a weight of 4
    def view_product(self):
        product_pk = randint(1, 1000)
        self.client.get(f"/store/products/{product_pk}/", name="/store/products/:pk")

    # Add product to cart
    @task(1)  # task with a weight of 1
    def add_to_cart(self):
        product_pk = randint(1, 10)
        self.client.post(
            f"/store/carts/{self.cart_pk}/items/",
            name="/store/carts/items",
            json={"product_id": product_pk, "quantity": 1},
        )

    @task  # task with a weight of 1
    def say_hello10(self):
        self.client.get(f"/playground/hello10/")

    def on_start(self):
        response = self.client.post("/store/carts/")
        result = response.json()
        self.cart_pk = result["pk"]
