import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from app.services.group_service import GroupService
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse
from app.db.models.catalog.group import Group


class TestGroupServiceSimple:
    """Simple test cases for GroupService"""

    @pytest.fixture
    def mock_session(self):
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def group_service(self, mock_session):
        """Group service instance with mocked session"""
        return GroupService(mock_session)

    def test_group_service_initialization(self, mock_session):
        """Test that GroupService initializes correctly"""
        service = GroupService(mock_session)
        assert service.repo is not None

    @pytest.mark.asyncio
    async def test_group_service_has_required_methods(self, group_service):
        """Test that GroupService has all required methods"""
        required_methods = [
            'create_group',
            'get_group_by_id', 
            'update_group',
            'delete_group',
            'get_all_groups',
            'get_groups_by_teacher_id'
        ]
        
        for method_name in required_methods:
            assert hasattr(group_service, method_name), f"Method {method_name} not found"

    def test_group_create_schema_validation(self):
        """Test GroupCreate schema validation"""
        # Valid data
        valid_data = GroupCreate(name="Test Group", size=30)
        assert valid_data.name == "Test Group"
        assert valid_data.size == 30

        # Invalid data - should raise validation error
        with pytest.raises(ValueError):
            GroupCreate(name="", size=30)  # Empty name

        with pytest.raises(ValueError):
            GroupCreate(name="Test Group", size=0)  # Invalid size

    def test_group_update_schema_validation(self):
        """Test GroupUpdate schema validation"""
        # Valid data
        valid_data = GroupUpdate(name="Updated Group", size=25)
        assert valid_data.name == "Updated Group"
        assert valid_data.size == 25

        # Partial update - should work
        partial_data = GroupUpdate(name="Updated Group")
        assert partial_data.name == "Updated Group"
        assert partial_data.size is None

    def test_group_response_schema_validation(self):
        """Test GroupResponse schema validation"""
        group_id = uuid4()
        response = GroupResponse(
            group_id=group_id,
            name="Test Group",
            size=30
        )
        assert response.group_id == group_id
        assert response.name == "Test Group"
        assert response.size == 30
