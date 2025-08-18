import pytest

from app import is_uniprot_id


def test_valid_uniprot_id():
    assert is_uniprot_id("P05067")


def test_invalid_uniprot_id_with_extra_text():
    assert not is_uniprot_id("P05067 extra")


def test_invalid_short_code():
    assert not is_uniprot_id("P53")
