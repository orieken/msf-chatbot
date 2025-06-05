import pytest

from core.repository import InMemoryAssignmentRepository
from core.services import AssignmentService


class TestAssignmentService:
    """Tests for the AssignmentService class."""

    @pytest.fixture
    def repository(self):
        """Create a repository for testing."""
        return InMemoryAssignmentRepository()

    @pytest.fixture
    def service(self, repository):
        """Create a service for testing."""
        return AssignmentService(repository)

    def test_assign_to_lane_success(self, service):
        """Test assigning a member to an empty lane."""
        # Arrange
        member = "user1"
        team_number = 1
        lane_number = 3

        # Act
        success, suggestion = service.assign_user(member, team_number, lane_number)

        # Assert
        assert success is True
        assert suggestion is None

    def test_assign_to_lane_nonexistent_team(self, service):
        """Test assigning a member to a nonexistent team."""
        # Arrange
        member = "user1"
        team_number = 10  # Non-existent team
        lane_number = 3

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            service.assign_user(member, team_number, lane_number)

        # Check that the error message mentions the team number
        assert f"Team number must be between 1 and 3, got {team_number}" in str(excinfo.value)

    def test_assign_to_lane_nonexistent_lane(self, service):
        """Test assigning a member to a nonexistent lane."""
        # Arrange
        member = "user1"
        team_number = 1
        lane_number = 15  # Non-existent lane

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            service.assign_user(member, team_number, lane_number)

        # Check that the error message mentions the lane number
        assert f"Lane number must be between 1 and 8, got {lane_number}" in str(excinfo.value)

    def test_assign_to_occupied_lane(self, service):
        """Test assigning a member to an already occupied lane."""
        # Arrange
        member1 = "user1"
        member2 = "user2"
        team_number = 1
        lane_number = 3

        # First assign member1
        service.assign_user(member1, team_number, lane_number)

        # Act - Try to assign member2 to the same lane
        success, suggestion = service.assign_user(member2, team_number, lane_number)

        # Assert
        assert success is False
        assert suggestion is not None  # Should suggest an alternative lane

    def test_assign_to_any_empty_success(self, service):
        """Test assigning a member to any empty lane."""
        # Arrange
        member = "user1"

        # Act
        slot = service.assign_random(member)

        # Assert
        assert slot is not None
        assert isinstance(slot, tuple)
        assert len(slot) == 2
        assert 1 <= slot[0] <= 3  # Team number should be between 1 and 3
        assert 1 <= slot[1] <= 8  # Lane number should be between 1 and 8

    def test_assign_to_any_empty_all_occupied(self, service):
        """Test assigning a member when all lanes are occupied."""
        # Arrange - Fill all lanes
        for team_number in range(1, 4):
            for lane_number in range(1, 9):
                service.assign_user(f"user{team_number}_{lane_number}", team_number, lane_number)

        # Act
        slot = service.assign_random("newuser")

        # Assert
        assert slot is None

    def test_remove_member_success(self, service):
        """Test removing a member from their assigned lanes."""
        # Arrange
        member = "user1"
        team_number = 2
        lane_number = 5

        # Assign the member first
        service.assign_user(member, team_number, lane_number)

        # Act
        removed = service.remove_user(member)

        # Assert
        assert removed is True

    def test_remove_nonexistent_member(self, service):
        """Test removing a member who is not assigned to any lane."""
        # Arrange
        member = "nonexistent"

        # Act
        removed = service.remove_user(member)

        # Assert
        assert removed is False

    def test_get_team_status(self, service, repository):
        """Test getting the status of all teams."""
        # Arrange
        member1 = "user1"
        team1 = 1
        lane1 = 3

        member2 = "user2"
        team2 = 2
        lane2 = 5

        # Assign members
        service.assign_user(member1, team1, lane1)
        service.assign_user(member2, team2, lane2)

        # Act
        assignments = service.list_all_assignments()

        # Assert
        assert f"{team1}-{lane1}" in assignments
        assert f"{team2}-{lane2}" in assignments

        # Check that the assignments contain the correct members
        assert assignments[f"{team1}-{lane1}"].user == member1
        assert assignments[f"{team2}-{lane2}"].user == member2

    def test_list_all_assignments(self, service):
        """Test listing all assignments."""
        # Arrange
        member1 = "user1"
        team1 = 1
        lane1 = 3

        member2 = "user2"
        team2 = 2
        lane2 = 5

        # Assign members
        service.assign_user(member1, team1, lane1)
        service.assign_user(member2, team2, lane2)

        # Act
        assignments = service.list_all_assignments()

        # Assert
        # Check that the assignments dictionary contains the expected keys
        assert f"{team1}-{lane1}" in assignments
        assert f"{team2}-{lane2}" in assignments

        # Check that the assignments contain the correct members
        assert assignments[f"{team1}-{lane1}"].user == member1
        assert assignments[f"{team2}-{lane2}"].user == member2

        # Check that the assignments have the correct team and lane numbers
        assert assignments[f"{team1}-{lane1}"].team == team1
        assert assignments[f"{team1}-{lane1}"].lane == lane1
        assert assignments[f"{team2}-{lane2}"].team == team2
        assert assignments[f"{team2}-{lane2}"].lane == lane2
