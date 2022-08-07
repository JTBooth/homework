import pytest
from ..flask_app.app import create_app

@pytest.fixture()
def app():
  app = create_app('test_settings.cfg')
  yield app

@pytest.fixture()
def client(app):
  return app.test_client()

@pytest.fixture()
def runner(app):
  return app.test_cli_runner()

# -----

def test_index(client):
  response = client.get("/")
  assert b'<header>Iroha Forms - Welcome</header>' in response.data