from fastapi.testclient import TestClient

from main import app


class TestPage:
    client = TestClient(app)

    def test_read_main(self):
        response = self.client.get("/")
        assert response.status_code == 200
        assert response.json() == {"msg": "Hello World"}

    def test_read_main2(self):
        response = self.client.get("/")
        assert response.status_code == 200
        assert response.json() == {"msg": "Hello World"}