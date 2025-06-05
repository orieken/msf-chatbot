from core.repository import InMemoryAssignmentRepository
from core.models import Assignment
from typing import Optional, Tuple

class AssignmentService:
    def __init__(self, repo: InMemoryAssignmentRepository):
        self.repo = repo

    def assign_user(self, user: str, team: int, lane: int) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """
        Try to assign a user to a specific lane. If it's unavailable,
        return a suggestion in the same team or elsewhere.
        """
        if self.repo.assign(user, team, lane):
            return True, None
        # Try other lanes on the same team
        for l in range(1, 9):
            if l != lane and self.repo.assign(user, team, l):
                return False, (team, l)
        # Try any lane globally
        alt = self.repo.find_first_empty()
        return False, alt

    def assign_random(self, user: str) -> Optional[Tuple[int, int]]:
        """
        Assign the user to the first available lane found.
        """
        slot = self.repo.find_first_empty()
        if slot:
            self.repo.assign(user, *slot)
        return slot

    def remove_user(self, user: str) -> bool:
        """
        Remove the user from their assigned lane.
        """
        return self.repo.remove(user)

    def find_user_assignment(self, user: str) -> Optional[Assignment]:
        """
        Return the user's current assignment if any.
        """
        return self.repo.find_assignment(user)

    def list_all_assignments(self):
        """
        Return all current assignments as a dictionary.
        """
        return self.repo.assignments

    def get_team_status(self):
        """
        Get the current status of all teams and their lanes.

        Returns:
            Dict[int, Dict[int, Optional[str]]]: Dictionary mapping team numbers to dictionaries
                mapping lane numbers to assigned members (or None if empty)
        """
        assignments = self.list_all_assignments()

        # Convert assignments to team status format
        team_status = {}
        for key, assignment in assignments.items():
            team = assignment.team
            lane = assignment.lane
            user = assignment.user

            if team not in team_status:
                team_status[team] = {}

            team_status[team][lane] = user

        return team_status
