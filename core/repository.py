import json
from typing import Dict, Optional, Tuple
from core.models import Assignment, TEAMS, LANES_PER_TEAM

class InMemoryAssignmentRepository:
    def __init__(self):
        # key: "team-lane" -> value: Assignment
        self.assignments: Dict[str, Assignment] = {}

    def assign(self, user: str, team: int, lane: int) -> bool:
        key = f"{team}-{lane}"
        # Check if lane is free
        if key not in self.assignments:
            # Ensure user isn't already assigned elsewhere
            self.remove(user)
            self.assignments[key] = Assignment(user, team, lane)
            return True
        return False

    def find_assignment(self, user: str) -> Optional[Assignment]:
        for a in self.assignments.values():
            if a.user == user:
                return a
        return None

    def remove(self, user: str) -> bool:
        found = False
        for k, v in list(self.assignments.items()):
            if v.user == user:
                del self.assignments[k]
                found = True
        return found

    def find_first_empty(self) -> Optional[Tuple[int, int]]:
        for t in range(1, TEAMS + 1):
            for l in range(1, LANES_PER_TEAM + 1):
                if f"{t}-{l}" not in self.assignments:
                    return (t, l)
        return None

class PersistentAssignmentRepository(InMemoryAssignmentRepository):
    def __init__(self, path='assignments.json'):
        self.path = path
        super().__init__()
        self.load()

    def assign(self, user, team, lane):
        if super().assign(user, team, lane):
            self.save()
            return True
        return False

    def remove(self, user):
        changed = super().remove(user)
        if changed:
            self.save()
        return changed

    def save(self):
        with open(self.path, 'w') as f:
            json.dump([a.__dict__ for a in self.assignments.values()], f)

    def load(self):
        try:
            with open(self.path) as f:
                data = json.load(f)
                for entry in data:
                    a = Assignment(**entry)
                    self.assignments[f"{a.team}-{a.lane}"] = a
        except FileNotFoundError:
            pass
