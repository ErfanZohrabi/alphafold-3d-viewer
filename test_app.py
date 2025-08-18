import pytest

from app import is_uniprot_id, app


def test_valid_uniprot_id():
    assert is_uniprot_id("P05067")


def test_invalid_uniprot_id_with_extra_text():
    assert not is_uniprot_id("P05067 extra")


def test_invalid_short_code():
    assert not is_uniprot_id("P53")


def test_index_page_examples_present():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "BRCA1" in html
