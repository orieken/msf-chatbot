import pytest
from core.repository import InMemoryAssignmentRepository
from core.services import AssignmentService
from interfaces.command_parser import CommandParser

@pytest.fixture
def team_lane_system():
    """Initialize the team lane system."""
    repository = InMemoryAssignmentRepository()
    service = AssignmentService(repository)
    command_parser = CommandParser(service)
    return {
        "repository": repository,
        "service": service,
        "command_parser": command_parser,
        "responses": [],
    }