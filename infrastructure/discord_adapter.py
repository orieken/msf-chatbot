from core.models import Assignment
from core.repository import PersistentAssignmentRepository
from core.services import AssignmentService
import shutil
import os

class DiscordAdapter:
    def __init__(self):
        self.repo = PersistentAssignmentRepository()
        self.service = AssignmentService(self.repo)

    def _parse_args(self, args: str):
        parts = args.strip().split()
        opts = {}
        i = 0
        while i < len(parts):
            if parts[i].startswith('--'):
                key = parts[i][2:]
                value = parts[i + 1] if i + 1 < len(parts) and not parts[i + 1].startswith('--') else True
                opts[key] = value
                i += 2 if isinstance(value, str) else 1
            else:
                i += 1
        return opts

    def handle_assign(self, ctx, args: str) -> str:
        user = ctx.author.name
        opts = self._parse_args(args)

        if 'member' in opts:
            user = opts['member']
        if 'random' in opts:
            result = self.service.assign_random(user)
            if result:
                return f"✅ {user} assigned to Team {result[0]} Lane {result[1]}"
            return "❌ No empty lanes available."
        if 'team' in opts and 'lane' in opts:
            try:
                team = int(opts['team'])
                lane = int(opts['lane'])
            except ValueError:
                return "❗ Invalid team or lane number."

            success, suggestion = self.service.assign_user(user, team, lane)
            if success:
                return f"✅ {user} assigned to Team {team} Lane {lane}"
            if suggestion:
                return f"❌ Lane taken. Suggested: Team {suggestion[0]} Lane {suggestion[1]}"
            return "❌ All lanes are full."

        return "❗ Invalid command format."

    def handle_remove(self, ctx, args: str) -> str:
        opts = self._parse_args(args)
        if 'member' not in opts:
            return "❗ Usage: remove --member <username>"
        removed = self.service.remove_user(opts['member'])
        if removed:
            return f"✅ {opts['member']} removed from lane."
        return f"❌ {opts['member']} was not assigned to any lane."

    def handle_backup(self) -> str:
        try:
            shutil.copyfile("assignments.json", "assignments_backup.json")
            return "✅ Backup created successfully."
        except Exception as e:
            return f"❌ Failed to create backup: {e}"

    def handle_reset(self) -> str:
        try:
            self.repo.assignments.clear()
            self.repo.save()
            return "✅ All assignments have been reset."
        except Exception as e:
            return f"❌ Failed to reset assignments: {e}"
