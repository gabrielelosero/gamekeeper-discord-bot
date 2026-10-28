"""Automatic welcome message for new members."""

import logging

import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("bot.welcome")


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = bot.config.welcome_channel_id
        self.template = bot.config.welcome_message

    def build_embed(self, member: discord.Member) -> discord.Embed:
        text = self.template.format(user=member.mention, server=member.guild.name)
        embed = discord.Embed(title=f"Welcome, {member.display_name}!", description=text, color=discord.Color.green())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"You are member #{member.guild.member_count}")
        return embed

    async def send_welcome(self, member: discord.Member) -> bool:
        """Send the welcome message to the configured channel. Returns False if that's not possible."""
        channel = member.guild.get_channel(self.channel_id) if self.channel_id else None
        if not isinstance(channel, discord.TextChannel):
            log.warning("Welcome channel not configured or not found (WELCOME_CHANNEL_ID=%s)", self.channel_id)
            return False

        try:
            # Mentioning the member in the message content sends them a notification.
            await channel.send(content=member.mention, embed=self.build_embed(member))
        except discord.Forbidden:
            log.warning("Missing permissions to write in #%s", channel.name)
            return False
        return True

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if not member.bot:
            await self.send_welcome(member)

    @app_commands.command(name="welcome-test", description="Send the welcome message for yourself, to preview it.")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def welcome_test(self, interaction: discord.Interaction) -> None:
        if await self.send_welcome(interaction.user):
            await interaction.response.send_message(f"Sent to <#{self.channel_id}>.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "I can't send the welcome message: check WELCOME_CHANNEL_ID in the .env file "
                "and make sure the bot can write in that channel.",
                ephemeral=True,
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Welcome(bot))
