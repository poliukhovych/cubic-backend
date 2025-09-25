import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from app.services.teacher_service import TeacherService
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse


class TestTeacherServiceSimple:
    """Simple test cases for TeacherService"""

    @pytest.fixture
    def mock_session(self):
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def teacher_service(self, mock_session):
        """Teacher service instance with mocked session"""
        return TeacherService(mock_session)

    def test_teacher_service_initialization(self, mock_session):
        """Test that TeacherService initializes correctly"""
        service = TeacherService(mock_session)
        assert service._repository is not None

    @pytest.mark.asyncio
    async def test_teacher_service_has_required_methods(self, teacher_service):
        """Test that TeacherService has all required methods"""
        required_methods = [
            'create_teacher',
            'get_teacher_by_id', 
            'get_teacher_by_user_id',
            'update_teacher',
            'delete_teacher',
            'get_all_teachers',
            'confirm_teacher'
        ]
        
        for method_name in required_methods:
            assert hasattr(teacher_service, method_name), f"Method {method_name} not found"

    def test_teacher_create_schema_validation(self):
        """Test TeacherCreate schema validation"""
        # Valid data
        valid_data = TeacherCreate(
            first_name="John",
            last_name="Doe",
            patronymic="Smith",
            confirmed=False
        )
        assert valid_data.first_name == "John"
        assert valid_data.last_name == "Doe"
        assert valid_data.patronymic == "Smith"
        assert valid_data.confirmed is False

        # Valid data with user_id
        user_id = uuid4()
        valid_data_with_user = TeacherCreate(
            first_name="Jane",
            last_name="Smith",
            patronymic="Doe",
            confirmed=True,
            user_id=user_id
        )
        assert valid_data_with_user.user_id == user_id
        assert valid_data_with_user.confirmed is True

        # Invalid data - should raise validation error
        with pytest.raises(ValueError):
            TeacherCreate(
                first_name="",  # Empty name
                last_name="Doe",
                patronymic="Smith"
            )

        with pytest.raises(ValueError):
            TeacherCreate(
                first_name="John",
                last_name="",  # Empty last name
                patronymic="Smith"
            )

    def test_teacher_update_schema_validation(self):
        """Test TeacherUpdate schema validation"""
        # Valid partial update
        partial_update = TeacherUpdate(first_name="Jane")
        assert partial_update.first_name == "Jane"
        assert partial_update.last_name is None
        assert partial_update.patronymic is None
        assert partial_update.confirmed is None

        # Valid full update
        user_id = uuid4()
        full_update = TeacherUpdate(
            first_name="Jane",
            last_name="Smith",
            patronymic="Doe",
            confirmed=True,
            user_id=user_id
        )
        assert full_update.first_name == "Jane"
        assert full_update.last_name == "Smith"
        assert full_update.patronymic == "Doe"
        assert full_update.confirmed is True
        assert full_update.user_id == user_id

        # Invalid data - should raise validation error
        with pytest.raises(ValueError):
            TeacherUpdate(first_name="")  # Empty name

    def test_teacher_response_schema_validation(self):
        """Test TeacherResponse schema validation"""
        teacher_id = uuid4()
        user_id = uuid4()
        
        response = TeacherResponse(
            teacher_id=teacher_id,
            first_name="John",
            last_name="Doe",
            patronymic="Smith",
            confirmed=True,
            user_id=user_id
        )
        assert response.teacher_id == teacher_id
        assert response.first_name == "John"
        assert response.last_name == "Doe"
        assert response.patronymic == "Smith"
        assert response.confirmed is True
        assert response.user_id == user_id

        # Response without user_id
        response_no_user = TeacherResponse(
            teacher_id=teacher_id,
            first_name="Jane",
            last_name="Smith",
            patronymic="Doe",
            confirmed=False,
            user_id=None
        )
        assert response_no_user.user_id is None
        assert response_no_user.confirmed is False

    def test_teacher_list_response_schema_validation(self):
        """Test TeacherListResponse schema validation"""
        teacher_id1 = uuid4()
        teacher_id2 = uuid4()
        
        teachers = [
            TeacherResponse(
                teacher_id=teacher_id1,
                first_name="John",
                last_name="Doe",
                patronymic="Smith",
                confirmed=False,
                user_id=None
            ),
            TeacherResponse(
                teacher_id=teacher_id2,
                first_name="Jane",
                last_name="Smith",
                patronymic="Doe",
                confirmed=True,
                user_id=None
            )
        ]
        
        from app.schemas.teacher import TeacherListResponse
        list_response = TeacherListResponse(teachers=teachers, total=2)
        
        assert len(list_response.teachers) == 2
        assert list_response.total == 2
        assert list_response.teachers[0].first_name == "John"
        assert list_response.teachers[1].first_name == "Jane"
