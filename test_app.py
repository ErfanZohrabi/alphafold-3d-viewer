import pytest
from app import app, is_uniprot_id, build_afdb_pdb_url, is_amino_acid_sequence


def test_health_endpoint():
    client = app.test_client()
    res = client.get('/api/health')
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_is_uniprot_id():
    assert is_uniprot_id('P05067')
    assert not is_uniprot_id('insulin')


def test_is_amino_acid_sequence():
    assert is_amino_acid_sequence('ACDEFGHIKL')
    assert not is_amino_acid_sequence('P05067')


def test_search_by_uniprot(monkeypatch):
    def fake_head(url, timeout=10):
        class R:
            status_code = 200
        return R()

    monkeypatch.setattr('app.requests.head', fake_head)
    client = app.test_client()
    res = client.post('/search', json={'query': 'P05067'})
    assert res.status_code == 200
    assert res.get_json() == {
        'accession': 'P05067',
        'pdb_url': build_afdb_pdb_url('P05067')
    }


def test_search_by_name(monkeypatch):
    def fake_lookup(name):
        return 'P01308'

    def fake_head(url, timeout=10):
        class R:
            status_code = 200
        return R()

    monkeypatch.setattr('app.uniprot_lookup_by_name', fake_lookup)
    monkeypatch.setattr('app.requests.head', fake_head)
    client = app.test_client()
    res = client.post('/search', json={'query': 'insulin'})
    assert res.status_code == 200
    assert res.get_json() == {
        'accession': 'P01308',
        'pdb_url': build_afdb_pdb_url('P01308')
    }


def test_sequence_search_returns_400():
    client = app.test_client()
    res = client.post('/search', json={'query': 'ACDEFGHIKL'})
    assert res.status_code == 400
    assert 'sequence' in res.get_json()['error'].lower()


def test_proxy_requires_url():
    client = app.test_client()
    res = client.get('/proxy')
    assert res.status_code == 400

