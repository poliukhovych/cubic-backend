from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestGroupAPISimple:

    def test_create_group_validation_error(self):
        """Test creating group with invalid data"""
        invalid_data = {
            "name": "",  # Empty name should fail validation
            "size": 30,
            "type": "bachelor",
            "course": 1
        }

        response = client.post("/api/groups/", json=invalid_data)
        assert response.status_code == 422  # Validation error
