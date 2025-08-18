import pytest
from app import is_uniprot_id, app

def test_set_query_triggers_search():
    client = app.test_client()
    response = client.get('/')
    html = response.get_data(as_text=True)
    start = html.find('function setQuery')
    end = html.find('}', start)
    assert 'search();' in html[start:end]

def test_search_endpoint_with_mock(monkeypatch):
    mock_data = {
        "id": "P05067",
        "model_url": "https://example.com/P05067.cif",
        "protein_name": "Amyloid beta",
    }

    def mock_fetch(uniprot_id):
        return mock_data

    monkeypatch.setattr('app.fetch_by_uniprot_id', mock_fetch)
    client = app.test_client()
    response = client.post('/search', json={"query": "P05067"})
    assert response.status_code == 200
    assert response.get_json() == mock_data

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
