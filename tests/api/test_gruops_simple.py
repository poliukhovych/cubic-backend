from fastapi.testclient import TestClient

from app.main import app
from app.core.security import get_current_user, get_current_admin

client = TestClient(app)


class TestGroupAPISimple:

    def test_create_group_requires_auth(self):
        response = client.post("/api/groups/", json={"name": "x", "size": 30, "type": "bachelor", "course": 1})
        assert response.status_code == 401

    def test_create_group_validation_error(self):
        """Test creating group with invalid data"""
        invalid_data = {
            "name": "",  # Empty name should fail validation
            "size": 30,
            "type": "bachelor",
            "course": 1
        }

        app.dependency_overrides[get_current_user] = lambda: object()
        app.dependency_overrides[get_current_admin] = lambda: object()
        try:
            response = client.post("/api/groups/", json=invalid_data)
        finally:
            app.dependency_overrides.clear()
        assert response.status_code == 422  # Validation error
