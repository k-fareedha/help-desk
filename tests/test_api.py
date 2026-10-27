import os
import tempfile
from fastapi.testclient import TestClient


def test_ticket_creation_and_listing():
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['DATABASE_PATH'] = os.path.join(tmp, 'test.db')
        import importlib
        import backend.main as main
        main = importlib.reload(main)
        with TestClient(main.app) as client:
            response = client.post('/tickets', json={'title': 'Test', 'description': 'Sample issue'})
            assert response.status_code == 200
            assert response.json()['status'] == 'open'
            listed = client.get('/tickets')
            assert listed.status_code == 200
            assert len(listed.json()) == 1
