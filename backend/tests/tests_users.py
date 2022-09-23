import pytest
from users.models import User


class TestUser:
    @pytest.mark.django_db
    def test_user_create(self):
        user = User.objects.create_user(
            email="test@email.ru",
            password="testpassword",
            first_name="testfirstname",
            last_name="testlastname",
            username="testusername",
        )
        assert User.objects.count() == 1
        assert user.email == "test@email.ru"
        assert user.first_name == "testfirstname"
        assert user.last_name == "testlastname"
        assert user.username == "testusername"

    @pytest.mark.django_db
    def test_create_user_without_email(self):
        count_after_create = User.objects.count()
        try:
            User.objects.create_user(
                password="testpassword",
                first_name="testfirstname",
                last_name="testlastname",
                username="Me",
            )
        except Exception as e:
            print(e)
        finally:
            count_before_create = User.objects.count()
            assert count_after_create == count_before_create
