from typing import Dict, List

from core.services import AssignmentService


class CommandParser:
    """Parser for Discord bot commands."""

    def __init__(self, service: AssignmentService):
        """
        Initialize the command parser with a service.

        Args:
            service: The service to use for executing commands
        """
        self._service = service
        self._command_handlers = {
            "assign": self._handle_assign,
            "remove": self._handle_remove,
            "list": self._handle_list,
        }

    def parse_and_execute(self, command: str, author: str, is_admin: bool = False) -> str:
        """
        Parse and execute a command.

        Args:
            command: The command to parse and execute
            author: The author of the command
            is_admin: Whether the author is an admin

        Returns:
            str: The response message
        """
        # Split the command into parts
        parts = command.strip().split()
        if not parts:
            return "Please provide a command."

        # Get the command name
        cmd_name = parts[0].lower()

        # Check if the command exists
        if cmd_name not in self._command_handlers:
            return f"Unknown command: {cmd_name}. Available commands: {', '.join(self._command_handlers.keys())}"

        # Parse arguments
        args = self._parse_args(parts[1:])

        # Execute the command
        return self._command_handlers[cmd_name](args, author, is_admin)

    def _parse_args(self, args: List[str]) -> Dict[str, str]:
        """
        Parse command arguments.

        Args:
            args: The arguments to parse

        Returns:
            Dict[str, str]: Dictionary of argument names to values
        """
        result = {}
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith("--"):
                arg_name = arg[2:]
                if i + 1 < len(args) and not args[i + 1].startswith("--"):
                    result[arg_name] = args[i + 1]
                    i += 2
                else:
                    result[arg_name] = "true"
                    i += 1
            else:
                i += 1
        return result

    def _handle_assign(self, args: Dict[str, str], author: str, is_admin: bool) -> str:
        """
        Handle the assign command.

        Args:
            args: The command arguments
            author: The author of the command
            is_admin: Whether the author is an admin

        Returns:
            str: The response message
        """
        # Check if the user is trying to assign someone else
        member = args.get("member")
        if member and not is_admin:
            return "Only admins can assign other members."

        # If no member is specified, use the author
        if not member:
            member = author

        # Check if the user wants to assign to any empty lane
        if "any-empty" in args or "random" in args:
            slot = self._service.assign_random(member)
            if slot:
                return f"Successfully assigned {member} to Team {slot[0]} Lane {slot[1]}"
            else:
                return "No empty lanes available."

        # Check if the user wants to assign to a specific lane
        if "team" in args and "lane" in args:
            try:
                team_number = int(args["team"])
                lane_number = int(args["lane"])

                success, suggestion = self._service.assign_user(member, team_number, lane_number)
                if success:
                    return f"Successfully assigned {member} to Team {team_number}, Lane {lane_number}."
                elif suggestion:
                    return f"Lane taken. Suggested: Team {suggestion[0]} Lane {suggestion[1]}"
                else:
                    return "All lanes are full."
            except ValueError as e:
                # Handle out-of-range team or lane numbers
                if "Team number must be between" in str(e):
                    return f"Team {team_number} does not exist. Teams are numbered 1-3."
                elif "Lane number must be between" in str(e):
                    return f"Lane {lane_number} does not exist. Lanes are numbered 1-8."
                else:
                    return "Team and lane numbers must be integers."

        return "Invalid assign command. Use --team and --lane to specify a lane, or --any-empty to assign to any empty lane."

    def _handle_remove(self, args: Dict[str, str], author: str, is_admin: bool) -> str:
        """
        Handle the remove command.

        Args:
            args: The command arguments
            author: The author of the command
            is_admin: Whether the author is an admin

        Returns:
            str: The response message
        """
        # Check if the user is trying to remove someone else
        member = args.get("member")
        if member and not is_admin:
            return "Only admins can remove other members."

        # If no member is specified, use the author
        if not member:
            member = author

        removed = self._service.remove_user(member)
        if removed:
            return f"Removed {member} from lane."
        else:
            return f"{member} is not assigned to any lanes."

    def _handle_list(self, args: Dict[str, str], author: str, is_admin: bool) -> str:
        """
        Handle the list command.

        Args:
            args: The command arguments
            author: The author of the command
            is_admin: Whether the author is an admin

        Returns:
            str: The response message with a formatted list of all team assignments
        """
        # Get the current status of all teams
        assignments = self._service.list_all_assignments()

        # Convert assignments to team status format
        team_status = {}
        for key, assignment in assignments.items():
            team = assignment.team
            lane = assignment.lane
            user = assignment.user

            if team not in team_status:
                team_status[team] = {}

            team_status[team][lane] = user

        if not team_status:
            return "No teams found."

        # Format the output
        output = ["**Current Team Assignments:**"]

        for team_number in sorted(team_status.keys()):
            team_lanes = team_status[team_number]
            team_line = f"**Team {team_number}**"
            output.append(team_line)

            # Count occupied lanes
            occupied_lanes = sum(1 for member in team_lanes.values() if member is not None)

            # Add lane information
            lane_lines = []
            for lane_number in sorted(team_lanes.keys()):
                member = team_lanes[lane_number]
                status = f"Lane {lane_number}: {member if member else 'Empty'}"
                lane_lines.append(status)

            # Add summary line
            summary = f"{occupied_lanes}/8 lanes filled"
            output.append(summary)

            # Add lane details
            output.extend(lane_lines)
            output.append("")  # Empty line between teams

        return "\n".join(output)
