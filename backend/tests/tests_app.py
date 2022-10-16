import pytest

from app.models import Tag


class TestTag:
    @pytest.mark.django_db
    def test_create_tag(
        self,
        test_name,
        test_color,
        test_slug,
    ):
        count_before_create = Tag.objects.count()
        Tag.objects.create(name=test_name, color=test_color, slug=test_slug)
        count_after_create = Tag.objects.count()
        assert count_before_create != count_after_create

    @pytest.mark.django_db
    def test_incorrect_color(self, test_name, test_slug):
        count_before_create = Tag.objects.count()
        try:
            tag = Tag(name=test_name, color="NOCOLOR", slug=test_slug)
            tag.full_clean()
            tag.save()
        except Exception:
            pass
        finally:
            count_after_create = Tag.objects.count()
            assert count_before_create == count_after_create
