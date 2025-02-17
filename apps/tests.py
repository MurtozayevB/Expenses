import pytest
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework.test import APIClient

from apps.models import User


@pytest.mark.django_db
class TestAuth:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def db(self):
        User.objects.create(fullname='Testhydguyfbsidfhbisdf', phone_number='+998991001143',password=make_password('123456789'))

    def test_register(self, client, db):
        url = reverse('register')
        data = {
            "fullname": "hjvjvd",
            "phone_number": "+998906677777",
            "password": "123456789"
        }
        response = client.post(url, data)
        assert response.status_code == 201


    # =========================================================================
    def test_login(self, client, db):
        url = reverse('token_obtain_pair')

        data = {"phone_number": "+998906677777", "password": "123456789"}

        response = client.post(url, data)

        assert response.status_code == 400

