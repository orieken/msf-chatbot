from dataclasses import dataclass
from typing import ClassVar
import discord

# Constants for team and lane structure
TEAMS: ClassVar[int] = 3
LANES_PER_TEAM: ClassVar[int] = 8

@dataclass
class Assignment:
    user: str
    team: int
    lane: int

    def __post_init__(self):
        if not (1 <= self.team <= TEAMS):
            raise ValueError(f"Team number must be between 1 and {TEAMS}, got {self.team}.")
        if not (1 <= self.lane <= LANES_PER_TEAM):
            raise ValueError(f"Lane number must be between 1 and {LANES_PER_TEAM}, got {self.lane}.")

    @staticmethod
    def format_assignments(assignments: list["Assignment"]) -> str:
        layout = {t: ["⬜" for _ in range(LANES_PER_TEAM)] for t in range(1, TEAMS + 1)}
        for a in assignments:
            layout[a.team][a.lane - 1] = a.user
        output = []
        for team, lanes in layout.items():
            row = f"Team {team}: " + " | ".join(f"{lane}" for lane in lanes)
            output.append(row)
        return "\n".join(output)

    @staticmethod
    def to_discord_embed(assignments: list["Assignment"]) -> discord.Embed:
        layout = {t: ["⬜" for _ in range(LANES_PER_TEAM)] for t in range(1, TEAMS + 1)}
        for a in assignments:
            layout[a.team][a.lane - 1] = a.user

        embed = discord.Embed(
            title="📋 Team Lane Assignments",
            description="Current team layout:",
            color=discord.Color.green()
        )

        for team, lanes in layout.items():
            display = " | ".join(lanes)
            embed.add_field(name=f"Team {team}", value=display, inline=False)

        return embed
