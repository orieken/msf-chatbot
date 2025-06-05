import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

from core.models import Assignment
from infrastructure.discord_adapter import DiscordAdapter

def main():
    ### bot.py
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    GUILD_ID = discord.Object(id=int(os.getenv("DISCORD_GUILD_ID")))

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="raid-", intents=intents)
    adapter = DiscordAdapter()

    @bot.event
    async def on_ready():
        await bot.tree.sync(guild=GUILD_ID)
        print(f"✅ Bot connected as {bot.user}")

    # Slash Command: /assign
    @bot.tree.command(name="assign", description="Assign a user to a team lane", guild=GUILD_ID)
    @app_commands.describe(
        team="Team number (1–3)",
        lane="Lane number (1–8)",
        member="Optional: user to assign",
        random="Assign to any available lane"
    )
    async def assign(interaction: discord.Interaction, team: int = None, lane: int = None, member: str = None,
                     random: bool = False):
        user = member or interaction.user.name
        if random:
            slot = adapter.service.assign_random(user)
            msg = f"✅ {user} assigned to Team {slot[0]} Lane {slot[1]}" if slot else "❌ No empty lanes available."
            await interaction.response.send_message(msg)
            return

        if team and lane:
            success, suggestion = adapter.service.assign_user(user, team, lane)
            if success:
                await interaction.response.send_message(f"✅ {user} assigned to Team {team} Lane {lane}")
            elif suggestion:
                await interaction.response.send_message(
                    f"❌ Lane taken. Suggested: Team {suggestion[0]} Lane {suggestion[1]}")
            else:
                await interaction.response.send_message("❌ All lanes are full.")
        else:
            await interaction.response.send_message("❗ You must provide either `team` and `lane`, or `random`.")

    # Slash Command: /remove
    @bot.tree.command(name="remove", description="Remove a user from their assigned lane", guild=GUILD_ID)
    @app_commands.describe(member="User to remove")
    async def remove(interaction: discord.Interaction, member: str):
        removed = adapter.service.remove_user(member)
        msg = f"✅ {member} removed from lane." if removed else f"❌ {member} was not assigned to any lane."
        await interaction.response.send_message(msg)

    # Optional: Legacy Text Commands
    @bot.command(name="assign")
    async def legacy_assign(ctx, *, args: str):
        result = adapter.handle_assign(ctx, args)
        await ctx.send(result)

    @bot.command(name="remove")
    async def legacy_remove(ctx, *, args: str):
        result = adapter.handle_remove(ctx, args)
        await ctx.send(result)

    # Slash command: /list
    @bot.tree.command(name="list", description="Show all current team lane assignments", guild=GUILD_ID)
    async def list_assignments(interaction: discord.Interaction):
        assignments = list(adapter.service.list_all_assignments().values())
        embed = Assignment.to_discord_embed(assignments)
        await interaction.response.send_message(embed=embed)

    # Text command: raid-list
    @bot.command(name="list")
    async def legacy_list(ctx):
        assignments = list(adapter.service.list_all_assignments().values())
        output = "```\n" + Assignment.format_assignments(assignments) + "\n```"
        await ctx.send(output)

    bot.run(TOKEN)


if __name__ == "__main__":
    main()
