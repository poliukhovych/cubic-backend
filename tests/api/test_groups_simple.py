import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
import time

from app.main import app

client = TestClient(app)


class TestGroupAPISimple:
    """Simple test cases for Group API endpoints without mocks"""

    def test_get_all_groups(self):
        """Test getting all groups"""
        response = client.get("/api/groups/")
        assert response.status_code == 200
        data = response.json()
        assert "groups" in data
        assert "total" in data
        assert isinstance(data["groups"], list)

    def test_create_group(self):
        """Test creating a group"""
        # Use unique name to avoid conflicts
        group_name = f"Test Group {int(time.time())}"
        group_data = {
            "name": group_name,
            "size": 30
        }
        
        response = client.post("/api/groups/", json=group_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == group_name
        assert data["size"] == 30
        assert "group_id" in data

    def test_create_group_validation_error(self):
        """Test creating group with invalid data"""
        invalid_data = {
            "name": "",  # Empty name should fail validation
            "size": 30
        }
        
        response = client.post("/api/groups/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_create_group_duplicate_name(self):
        """Test creating group with duplicate name"""
        group_name = f"Duplicate Test Group {int(time.time())}"
        group_data = {
            "name": group_name,
            "size": 30
        }
        
        # Create first group
        response1 = client.post("/api/groups/", json=group_data)
        assert response1.status_code == 201
        
        # Try to create second group with same name
        response2 = client.post("/api/groups/", json=group_data)
        assert response2.status_code == 400  # Should fail due to unique constraint

    def test_get_group_by_id_not_found(self):
        """Test getting group by non-existent ID"""
        fake_id = uuid4()
        response = client.get(f"/api/groups/{fake_id}")
        assert response.status_code == 404

    def test_update_group_not_found(self):
        """Test updating non-existent group"""
        fake_id = uuid4()
        update_data = {"name": "Updated Group"}
        response = client.put(f"/api/groups/{fake_id}", json=update_data)
        assert response.status_code == 404

    def test_delete_group_not_found(self):
        """Test deleting non-existent group"""
        fake_id = uuid4()
        response = client.delete(f"/api/groups/{fake_id}")
        assert response.status_code == 404
