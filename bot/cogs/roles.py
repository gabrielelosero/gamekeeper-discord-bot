"""Self-assignable roles: a panel with one button per role."""

import re

import discord
from discord import app_commands
from discord.ext import commands


class RoleButton(discord.ui.DynamicItem[discord.ui.Button], template=r"selfrole:(?P<role_id>\d+)"):
    """Button that adds or removes a role for whoever clicks it.

    The role ID is stored in the button's custom_id, so panels that were already
    posted keep working after a restart, with no database needed.
    """

    def __init__(self, role_id: int, label: str = "Role"):
        self.role_id = role_id
        super().__init__(
            discord.ui.Button(
                label=label,
                style=discord.ButtonStyle.secondary,
                custom_id=f"selfrole:{role_id}",
            )
        )

    @classmethod
    async def from_custom_id(
        cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str]
    ) -> "RoleButton":
        # Called by discord.py when someone clicks a "selfrole:<id>" button.
        return cls(int(match["role_id"]), label=item.label or "Role")

    async def callback(self, interaction: discord.Interaction) -> None:
        member = interaction.user
        role = interaction.guild.get_role(self.role_id)
        if role is None:
            await interaction.response.send_message("This role no longer exists.", ephemeral=True)
            return

        try:
            if role in member.roles:
                await member.remove_roles(role, reason="Self-assigned role")
                message = f"Role {role.mention} removed."
            else:
                await member.add_roles(role, reason="Self-assigned role")
                message = f"Role {role.mention} added."
        except discord.Forbidden:
            message = "I don't have permission to manage this role: please contact an admin."

        await interaction.response.send_message(message, ephemeral=True)


class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        # Register the dynamic button: it handles clicks on both old and new panels.
        self.bot.add_dynamic_items(RoleButton)

    async def cog_unload(self) -> None:
        self.bot.remove_dynamic_items(RoleButton)

    @app_commands.command(name="roles", description="Post a panel with buttons to self-assign roles.")
    @app_commands.describe(
        role1="First role",
        role2="Second role (optional)",
        role3="Third role (optional)",
        role4="Fourth role (optional)",
        role5="Fifth role (optional)",
        title="Panel title",
    )
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.guild_only()
    async def role_panel(
        self,
        interaction: discord.Interaction,
        role1: discord.Role,
        role2: discord.Role | None = None,
        role3: discord.Role | None = None,
        role4: discord.Role | None = None,
        role5: discord.Role | None = None,
        title: str = "Pick your roles",
    ) -> None:
        # Drop empty parameters and duplicates, keeping the order.
        roles = list(dict.fromkeys(r for r in (role1, role2, role3, role4, role5) if r))

        # The bot can only manage regular roles that sit below its own highest role.
        bot_top = interaction.guild.me.top_role
        invalid = [r for r in roles if r.is_default() or r.managed or r >= bot_top]
        if invalid:
            names = ", ".join(r.mention for r in invalid)
            await interaction.response.send_message(
                f"I can't assign: {names}.\n"
                f"In the server settings, move the **{bot_top.name}** role above these roles "
                "(and don't use @everyone or bot roles).",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=title,
            description="Click a button to get the role, click it again to remove it.\n\n"
            + "\n".join(f"• {r.mention}" for r in roles),
            color=discord.Color.blurple(),
        )
        view = discord.ui.View(timeout=None)
        for role in roles:
            view.add_item(RoleButton(role.id, label=role.name))

        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("Panel posted.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Roles(bot))
