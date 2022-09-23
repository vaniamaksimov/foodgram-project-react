import uuid
import pytest


@pytest.fixture
def test_password():
    return "test_password"


@pytest.fixture
def test_email():
    return "test@mail.com"


@pytest.fixture
def test_first_name():
    return "test_first_name"


@pytest.fixture
def test_last_name():
    return "test_last_name"


@pytest.fixture
def test_username():
    return "test_username"


@pytest.fixture
def create_user(db, django_user_model):
    def make_user(**kwargs):
        kwargs["password"] = "password"
        kwargs["username"] = "username"
        kwargs["email"] = "email@email.ru"
        kwargs["first_name"] = "firstname"
        kwargs["last_name"] = "lastname"
        return django_user_model.objects.create_user(**kwargs)

    return make_user
