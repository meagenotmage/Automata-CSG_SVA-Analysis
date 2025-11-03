import json
import pytest
from importlib import util as importlib_util
import os


def load_app_module():
    """Dynamically load the Flask app module."""
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app.py'))
    spec = importlib_util.spec_from_file_location('app', app_path)
    module = importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app = load_app_module()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the /health endpoint returns ok status."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'service' in data


def test_parse_endpoint_mismatch(client):
    """Test /parse endpoint detects subject-verb disagreement."""
    response = client.post('/parse', 
                          json={'sentence': 'The cats runs.'},
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'cats' in data['message']
    assert 'runs' in data['message']
    assert 'problem_spans' in data
    assert len(data['problem_spans']) > 0


def test_parse_endpoint_ok_singular(client):
    """Test /parse endpoint accepts correct singular agreement."""
    response = client.post('/parse',
                          json={'sentence': 'The cat runs.'},
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


def test_parse_endpoint_ok_plural(client):
    """Test /parse endpoint accepts correct plural agreement."""
    response = client.post('/parse',
                          json={'sentence': 'The cats run.'},
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


def test_parse_endpoint_missing_sentence(client):
    """Test /parse endpoint handles missing sentence gracefully."""
    response = client.post('/parse',
                          json={},
                          content_type='application/json')
    assert response.status_code == 200
    # Should still return something, even if it's an error


def test_parse_tree_structure(client):
    """Test that /parse returns a proper parse tree structure."""
    response = client.post('/parse',
                          json={'sentence': 'The cat runs.'},
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'parse_tree' in data
    tree = data['parse_tree']
    assert 'label' in tree
    assert 'children' in tree
    assert tree['label'] == 'S'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
