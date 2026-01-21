"""Unit tests for OrganizationService."""

import pytest
from unittest.mock import Mock, AsyncMock

from app.models.organization import Organization
from app.repositories.interfaces import IOrganizationRepository
from app.services.interfaces import IHashService
from app.services.organization_service import OrganizationService


class TestOrganizationService:
    @pytest.fixture
    def mock_organization_repository(self):
        return Mock(spec=IOrganizationRepository)

    @pytest.fixture
    def mock_hash_service(self):
        return Mock(spec=IHashService)

    @pytest.fixture
    def organization_service(self, mock_organization_repository, mock_hash_service):
        return OrganizationService(
            organization_repository=mock_organization_repository,
            hash_service=mock_hash_service,
        )

    @pytest.mark.asyncio
    async def test_get_organization_by_name_success(
        self, organization_service, mock_organization_repository
    ):
        # Arrange
        name = "Test Org"
        org = Organization(id=1, name=name)
        mock_organization_repository.get_by_name = AsyncMock(return_value=org)

        # Act
        result = await organization_service.get_organization_by_name(name)

        # Assert
        assert result == org
        mock_organization_repository.get_by_name.assert_called_once_with(name)

    @pytest.mark.asyncio
    async def test_get_organization_by_name_not_found(
        self, organization_service, mock_organization_repository
    ):
        # Arrange
        name = "None Org"
        mock_organization_repository.get_by_name = AsyncMock(return_value=None)

        # Act
        result = await organization_service.get_organization_by_name(name)

        # Assert
        assert result is None
        mock_organization_repository.get_by_name.assert_called_once_with(name)

    @pytest.mark.asyncio
    async def test_add_user_to_organization_success(
        self, organization_service, mock_organization_repository
    ):
        # Arrange
        org_id = 1
        user_id = 10
        org = Organization(id=org_id, name="Org")
        mock_organization_repository.add_user_to_organization = AsyncMock(return_value=org)

        # Act
        result = await organization_service.add_user_to_organization(org_id, user_id)

        # Assert
        assert result == org
        mock_organization_repository.add_user_to_organization.assert_called_once_with(
            org_id, user_id
        )

    @pytest.mark.asyncio
    async def test_add_user_to_organization_failure(
        self, organization_service, mock_organization_repository
    ):
        # Arrange
        org_id = 999
        user_id = 10
        mock_organization_repository.add_user_to_organization = AsyncMock(return_value=None)

        # Act
        result = await organization_service.add_user_to_organization(org_id, user_id)

        # Assert
        assert result is None
        mock_organization_repository.add_user_to_organization.assert_called_once_with(
            org_id, user_id
        )
