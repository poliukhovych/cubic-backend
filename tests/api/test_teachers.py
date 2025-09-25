import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.main import app
from app.schemas.teacher import TeacherResponse, TeacherCreate, TeacherUpdate

client = TestClient(app)


@pytest.fixture
def mock_teacher_service():
    """Mock teacher service for testing"""
    with patch('app.api.teachers.get_teacher_service') as mock:
        mock_service = AsyncMock()
        mock.return_value = mock_service
        yield mock_service


@pytest.fixture
def sample_teacher_data():
    """Sample teacher creation data"""
    return {
        "first_name": "John",
        "last_name": "Doe", 
        "patronymic": "Smith",
        "confirmed": False
    }


@pytest.fixture
def sample_teacher_response():
    """Sample teacher response for testing"""
    teacher_id = uuid4()
    return TeacherResponse(
        teacher_id=teacher_id,
        first_name="John",
        last_name="Doe",
        patronymic="Smith",
        confirmed=False,
        user_id=None
    )


class TestTeacherAPI:
    """Simple test cases for Teacher API endpoints"""

    @pytest.mark.asyncio
    async def test_get_all_teachers_success(self, mock_teacher_service, sample_teacher_response):
        """Test getting all teachers successfully"""
        # Arrange
        mock_teacher_service.get_all_teachers.return_value = [sample_teacher_response]
        
        # Act
        response = client.get("/api/teachers/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "teachers" in data
        assert "total" in data
        assert len(data["teachers"]) == 1
        assert data["teachers"][0]["first_name"] == "John"
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_get_teacher_by_id_success(self, mock_teacher_service, sample_teacher_response):
        """Test getting teacher by ID successfully"""
        # Arrange
        teacher_id = sample_teacher_response.teacher_id
        mock_teacher_service.get_teacher_by_id.return_value = sample_teacher_response
        
        # Act
        response = client.get(f"/api/teachers/{teacher_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["teacher_id"] == str(teacher_id)
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"

    @pytest.mark.asyncio
    async def test_get_teacher_by_id_not_found(self, mock_teacher_service):
        """Test getting teacher by ID when teacher doesn't exist"""
        # Arrange
        teacher_id = uuid4()
        mock_teacher_service.get_teacher_by_id.return_value = None
        
        # Act
        response = client.get(f"/api/teachers/{teacher_id}")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_teacher_by_user_id_success(self, mock_teacher_service, sample_teacher_response):
        """Test getting teacher by user ID successfully"""
        # Arrange
        user_id = uuid4()
        mock_teacher_service.get_teacher_by_user_id.return_value = sample_teacher_response
        
        # Act
        response = client.get(f"/api/teachers/user/{user_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"

    @pytest.mark.asyncio
    async def test_get_teacher_by_user_id_not_found(self, mock_teacher_service):
        """Test getting teacher by user ID when teacher doesn't exist"""
        # Arrange
        user_id = uuid4()
        mock_teacher_service.get_teacher_by_user_id.return_value = None
        
        # Act
        response = client.get(f"/api/teachers/user/{user_id}")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_teacher_success(self, mock_teacher_service, sample_teacher_data, sample_teacher_response):
        """Test creating teacher successfully"""
        # Arrange
        mock_teacher_service.create_teacher.return_value = sample_teacher_response
        
        # Act
        response = client.post("/api/teachers/", json=sample_teacher_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == sample_teacher_data["first_name"]
        assert data["last_name"] == sample_teacher_data["last_name"]
        assert data["patronymic"] == sample_teacher_data["patronymic"]
        assert data["confirmed"] == sample_teacher_data["confirmed"]

    @pytest.mark.asyncio
    async def test_create_teacher_validation_error(self, mock_teacher_service):
        """Test creating teacher with invalid data"""
        # Arrange
        invalid_data = {
            "first_name": "",  # Empty name should fail validation
            "last_name": "Doe",
            "patronymic": "Smith"
        }
        mock_teacher_service.create_teacher.side_effect = Exception("Validation error")
        
        # Act
        response = client.post("/api/teachers/", json=invalid_data)
        
        # Assert
        assert response.status_code == 400
        assert "Failed to create teacher" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_teacher_success(self, mock_teacher_service, sample_teacher_response):
        """Test updating teacher successfully"""
        # Arrange
        teacher_id = sample_teacher_response.teacher_id
        update_data = {"first_name": "Jane", "confirmed": True}
        updated_teacher = TeacherResponse(
            teacher_id=teacher_id,
            first_name="Jane",
            last_name=sample_teacher_response.last_name,
            patronymic=sample_teacher_response.patronymic,
            confirmed=True,
            user_id=sample_teacher_response.user_id
        )
        mock_teacher_service.update_teacher.return_value = updated_teacher
        
        # Act
        response = client.put(f"/api/teachers/{teacher_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["confirmed"] is True

    @pytest.mark.asyncio
    async def test_update_teacher_not_found(self, mock_teacher_service):
        """Test updating teacher that doesn't exist"""
        # Arrange
        teacher_id = uuid4()
        update_data = {"first_name": "Jane"}
        mock_teacher_service.update_teacher.return_value = None
        
        # Act
        response = client.put(f"/api/teachers/{teacher_id}", json=update_data)
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_confirm_teacher_success(self, mock_teacher_service, sample_teacher_response):
        """Test confirming teacher successfully"""
        # Arrange
        teacher_id = sample_teacher_response.teacher_id
        confirmed_teacher = TeacherResponse(
            teacher_id=teacher_id,
            first_name=sample_teacher_response.first_name,
            last_name=sample_teacher_response.last_name,
            patronymic=sample_teacher_response.patronymic,
            confirmed=True,
            user_id=sample_teacher_response.user_id
        )
        mock_teacher_service.confirm_teacher.return_value = confirmed_teacher
        
        # Act
        response = client.patch(f"/api/teachers/{teacher_id}/confirm")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["confirmed"] is True

    @pytest.mark.asyncio
    async def test_confirm_teacher_not_found(self, mock_teacher_service):
        """Test confirming teacher that doesn't exist"""
        # Arrange
        teacher_id = uuid4()
        mock_teacher_service.confirm_teacher.return_value = None
        
        # Act
        response = client.patch(f"/api/teachers/{teacher_id}/confirm")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_teacher_success(self, mock_teacher_service):
        """Test deleting teacher successfully"""
        # Arrange
        teacher_id = uuid4()
        mock_teacher_service.delete_teacher.return_value = True
        
        # Act
        response = client.delete(f"/api/teachers/{teacher_id}")
        
        # Assert
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_teacher_not_found(self, mock_teacher_service):
        """Test deleting teacher that doesn't exist"""
        # Arrange
        teacher_id = uuid4()
        mock_teacher_service.delete_teacher.return_value = False
        
        # Act
        response = client.delete(f"/api/teachers/{teacher_id}")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_teacher_courses(self, mock_teacher_service):
        """Test getting teacher courses (TODO endpoint)"""
        # Arrange
        teacher_id = uuid4()
        
        # Act
        response = client.get(f"/api/teachers/{teacher_id}/courses")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == []  # Currently returns empty list

    @pytest.mark.asyncio
    async def test_get_teacher_groups(self, mock_teacher_service):
        """Test getting teacher groups (TODO endpoint)"""
        # Arrange
        teacher_id = uuid4()
        
        # Act
        response = client.get(f"/api/teachers/{teacher_id}/groups")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == []  # Currently returns empty list
