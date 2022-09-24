import pytest

from users.models import User


class TestUser:
    @pytest.mark.django_db
    def test_create_user(
        self,
        test_password,
        test_email,
        test_first_name,
        test_last_name,
        test_username,
    ):
        count_before_create = User.objects.count()
        user = User.objects.create_user(
            email=test_email,
            password=test_password,
            first_name=test_first_name,
            last_name=test_last_name,
            username=test_username,
        )
        count_after_create = User.objects.count()
        assert (
            count_before_create != count_after_create
        ), "Пользователь не создался, проверьте создание пользователя"
        assert (
            user.email == test_email
        ), "Электронная почта не соответствует ожидаемой, проверьте создание пользователя"
        assert (
            user.first_name == test_first_name
        ), "Имя пользователя не соответствует ожидаемому, проверьте создание пользователя"
        assert (
            user.last_name == test_last_name
        ), "Фамилия пользователя не соответсвует ожидаемой, проверьте создание пользователя"
        assert (
            user.username == test_username
        ), "Никнейм пользователя не соотвествует ожидаемому, проверьте создание пользователя"

    @pytest.mark.django_db
    def test_create_user_without_email(
        self, test_password, test_first_name, test_last_name, test_username
    ):
        count_after_create = User.objects.count()
        try:
            User.objects.create_user(
                password=test_password,
                first_name=test_first_name,
                last_name=test_last_name,
                username=test_username,
            )
        except Exception:
            pass
        finally:
            count_before_create = User.objects.count()
            assert count_after_create == count_before_create

    @pytest.mark.django_db
    def test_create_user_without_name(
        self, test_email, test_password, test_last_name, test_username
    ):
        count_after_create = User.objects.count()
        try:
            User.objects.create_user(
                email=test_email,
                password=test_password,
                last_name=test_last_name,
                username=test_username,
            )
        except Exception:
            pass
        finally:
            count_before_create = User.objects.count()
            assert count_after_create == count_before_create

    @pytest.mark.django_db
    def test_create_user_without_lastname(
        self, test_email, test_password, test_first_name, test_username
    ):
        count_after_create = User.objects.count()
        try:
            User.objects.create_user(
                email=test_email,
                password=test_password,
                first_name=test_first_name,
                username=test_username,
            )
        except Exception:
            pass
        finally:
            count_before_create = User.objects.count()
            assert count_after_create == count_before_create

    @pytest.mark.django_db
    def test_create_user_without_username(
        self, test_email, test_password, test_first_name, test_last_name
    ):
        count_after_create = User.objects.count()
        try:
            User.objects.create_user(
                email=test_email,
                password=test_password,
                first_name=test_first_name,
                last_name=test_last_name,
            )
        except Exception:
            pass
        finally:
            count_before_create = User.objects.count()
            assert count_after_create == count_before_create
