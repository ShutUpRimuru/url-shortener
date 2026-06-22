import pytest
from app.main import app, redis_client

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    redis_client.flushdb()

def test_shorten_valid_url(client):
    response = client.post('/shorten', json={'url': 'https://example.com'})
    assert response.status_code == 201
    assert 'short_code' in response.get_json()

def test_shorten_invalid_url(client):
    response = client.post('/shorten', json={'url': 'not-a-valid-url'})
    assert response.status_code == 400

def test_redirect(client):
    post_res = client.post('/shorten', json={'url': 'https://example.com'})
    short_code = post_res.get_json()['short_code']

    get_res = client.get(f'/{short_code}')
    assert get_res.status_code == 302
    assert get_res.headers['Location'] == 'https://example.com'

def test_custom_code(client):
    response = client.post('/shorten', json={
        'url': 'https://example.com',
        'custom_code': 'my-custom-link'
    })
    assert response.status_code == 201
    assert response.get_json()['short_code'] == 'my-custom-link'
