import pytest


@pytest.fixture
def test_name():
    return "test_name"


@pytest.fixture
def test_color():
    return "#000000"


@pytest.fixture
def test_slug():
    return "test_slug"
