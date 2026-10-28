"""Comandi generali: /ping e /info."""

import platform
import time

import discord
from discord import app_commands
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.started_at = time.monotonic()

    @app_commands.command(name="ping", description="Controlla che il bot risponda e mostra la latenza.")
    async def ping(self, interaction: discord.Interaction) -> None:
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latenza: **{latency_ms} ms**", ephemeral=True)

    @app_commands.command(name="info", description="Informazioni sul bot.")
    async def info(self, interaction: discord.Interaction) -> None:
        uptime = int(time.monotonic() - self.started_at)
        hours, rest = divmod(uptime, 3600)
        minutes, seconds = divmod(rest, 60)

        embed = discord.Embed(
            title=self.bot.user.name,
            description="Bot di esempio per community di gioco: ruoli, benvenuto e stato del server.",
            color=discord.Color.blurple(),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="Server", value=str(len(self.bot.guilds)))
        embed.add_field(name="Uptime", value=f"{hours}h {minutes}m {seconds}s")
        embed.add_field(name="Latenza", value=f"{round(self.bot.latency * 1000)} ms")
        embed.set_footer(text=f"discord.py {discord.__version__} · Python {platform.python_version()}")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
