"""Step definitions for the assign.feature file."""
from pytest_bdd import given, when, then, parsers

from core.repository import InMemoryAssignmentRepository
from core.services import AssignmentService
from interfaces.command_parser import CommandParser


@given("the team lane system is initialized")
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


@given("all lanes are empty")
def all_lanes_empty(team_lane_system):
    """Ensure all lanes are empty."""
    # This is the default state of the system, so no action needed
    pass


@given(parsers.parse("team {team:d} lane {lane:d} is empty"))
def team_lane_is_empty(team_lane_system, team, lane):
    """Ensure a specific team lane is empty."""
    # This is the default state of the system, so no action needed
    pass


@given(parsers.parse('"{member}" is assigned to team {team:d} lane {lane:d}'))
def member_is_assigned(team_lane_system, member, team, lane):
    """Assign a member to a specific team lane."""
    service = team_lane_system["service"]
    service.assign_user(member, team, lane)


@given(parsers.parse('"{member}" is not assigned'))
def member_is_not_assigned(team_lane_system, member):
    """Ensure a member is not assigned to any lane."""
    # This is the default state of the system, so no action needed
    pass


@given("there are available lanes")
def available_lanes(team_lane_system):
    """Ensure there are available lanes."""
    # This is the default state of the system, so no action needed
    pass


@given("all lanes are occupied")
def all_lanes_occupied(team_lane_system):
    """Fill all lanes with members."""
    service = team_lane_system["service"]
    for team_number in range(1, 4):
        for lane_number in range(1, 9):
            service.assign_user(f"user{team_number}_{lane_number}", team_number, lane_number)


@when(parsers.parse('the user "{member}" runs "{command}"'))
def user_runs_command(team_lane_system, member, command):
    """Run a command as a user."""
    command_parser = team_lane_system["command_parser"]
    response = command_parser.parse_and_execute(command, member, is_admin=False)
    team_lane_system["responses"].append(response)
    team_lane_system["last_member"] = member


@when(parsers.parse('the admin runs "{command}"'))
def admin_runs_command(team_lane_system, command):
    """Run a command as an admin."""
    command_parser = team_lane_system["command_parser"]
    response = command_parser.parse_and_execute(command, "admin", is_admin=True)
    team_lane_system["responses"].append(response)


@then(parsers.parse('"{member}" should be assigned to team {team:d} lane {lane:d}'))
def member_should_be_assigned(team_lane_system, member, team, lane):
    """Check if a member is assigned to a specific team lane."""
    service = team_lane_system["service"]
    status = service.get_team_status()
    assert status[team][lane] == member


@then(parsers.parse('"{member}" should not be assigned to team {team:d} lane {lane:d}'))
def member_should_not_be_assigned(team_lane_system, member, team, lane):
    """Check if a member is not assigned to a specific team lane."""
    service = team_lane_system["service"]
    status = service.get_team_status()
    assert status[team][lane] != member


@then(parsers.parse('"{member}" should be assigned to a lane'))
def member_should_be_assigned_to_a_lane(team_lane_system, member):
    """Check if a member is assigned to any lane."""
    service = team_lane_system["service"]
    assignments = service.get_team_status()

    # Check if the member is assigned to any lane
    is_assigned = False
    for team_lanes in assignments.values():
        for assigned_member in team_lanes.values():
            if assigned_member == member:
                is_assigned = True
                break
        if is_assigned:
            break

    assert is_assigned


@then(parsers.parse('"{member}" is assigned to team {team:d} lane {lane:d}'))
def member_is_assigned_to_team_lane(team_lane_system, member, team, lane):
    """Check if a member is assigned to a specific team lane."""
    member_should_be_assigned(team_lane_system, member, team, lane)


@then(parsers.parse('"{member}" is no longer assigned to any lane'))
def member_is_no_longer_assigned(team_lane_system, member):
    """Check if a member is not assigned to any lane."""
    service = team_lane_system["service"]
    assignments = service.get_team_status()

    # Check if the member is not assigned to any lane
    is_assigned = False
    for team_lanes in assignments.values():
        for assigned_member in team_lanes.values():
            if assigned_member == member:
                is_assigned = True
                break
        if is_assigned:
            break

    assert not is_assigned


@then(parsers.parse('the system should respond with "{expected_response}"'))
def system_should_respond_with(team_lane_system, expected_response):
    """Check if the system responded with the expected message."""
    assert expected_response in team_lane_system["responses"][-1]


@then(parsers.parse('the system should respond with a message containing "{expected_substring}"'))
def system_should_respond_with_substring(team_lane_system, expected_substring):
    """Check if the system response contains the expected substring."""
    assert expected_substring in team_lane_system["responses"][-1]


@then("the system should respond with a success message")
def system_should_respond_with_success(team_lane_system):
    """Check if the system responded with a success message."""
    assert "Successfully" in team_lane_system["responses"][-1]


@then("the system should suggest alternative lanes")
def system_should_suggest_alternatives(team_lane_system):
    """Check if the system suggested alternative lanes."""
    assert "Suggested:" in team_lane_system["responses"][-1]
