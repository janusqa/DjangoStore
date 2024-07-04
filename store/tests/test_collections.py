from store.models import Collection
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
import pytest


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self):
        # AAA (Arrange, Act, Assert)
        # Arrange - Prepare System under test
        ## Create objects, put db in inital state etc.

        # Act - Kick off the behaviour to be tested
        ## eg. send request to server
        api_client = APIClient()
        response = api_client.post("/store/collections/", {"title": "a"})

        # Assert - Check if the behviour we expect occurs
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self):
        # AAA (Arrange, Act, Assert)
        # Arrange - Prepare System under test
        ## Create objects, put db in inital state etc.

        # Act - Kick off the behaviour to be tested
        ## eg. send request to server
        api_client = APIClient()
        api_client.force_authenticate(user={})  # authenticate user
        response = api_client.post("/store/collections/", {"title": "a"})

        # Assert - Check if the behviour we expect occurs
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self):
        # AAA (Arrange, Act, Assert)
        # Arrange - Prepare System under test
        ## Create objects, put db in inital state etc.

        # Act - Kick off the behaviour to be tested
        ## eg. send request to server
        api_client = APIClient()
        api_client.force_authenticate(user=User(is_staff=True))
        response = api_client.post("/store/collections/", {"title": ""})

        # Assert - Check if the behviour we expect occurs
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None

    def test_if_data_is_valid_returns_201(self):
        # AAA (Arrange, Act, Assert)
        # Arrange - Prepare System under test
        ## Create objects, put db in inital state etc.

        # Act - Kick off the behaviour to be tested
        ## eg. send request to server
        api_client = APIClient()
        api_client.force_authenticate(user=User(is_staff=True))
        response = api_client.post("/store/collections/", {"title": "a"})

        # Assert - Check if the behviour we expect occurs
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["pk"] > 0


@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_returns_200(self):
        api_client = APIClient()
        collection = Collection.objects.create(title="a")

        response = api_client.get(f"/store/collections/{collection.pk}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "pk": collection.pk,
            "title": collection.title,
            "product_count": 0,
        }
