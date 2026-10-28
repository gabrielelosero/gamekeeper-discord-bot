"""/status: status of a Minecraft (Java) server and online players."""

import asyncio
import base64
import io
import logging

import discord
from discord import app_commands
from discord.ext import commands
from mcstatus import JavaServer

log = logging.getLogger("bot.status")

QUERY_TIMEOUT = 5  # seconds
MAX_PLAYER_NAMES = 20


class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        config = bot.config
        # Default address: "host:port" from the .env file, if configured.
        self.default_address = f"{config.mc_host}:{config.mc_port}" if config.mc_host else None

    @app_commands.command(name="status", description="Show whether the Minecraft server is online and who's playing.")
    @app_commands.describe(address="Server address (e.g. play.example.com); if empty, uses the configured one")
    async def status(self, interaction: discord.Interaction, address: str | None = None) -> None:
        address = (address or self.default_address or "").strip()
        if not address:
            await interaction.response.send_message(
                "No server configured: set MC_HOST in the .env file or pass an address.",
                ephemeral=True,
            )
            return

        # The query can take a few seconds: Discord expects a response within 3.
        await interaction.response.defer()

        try:
            server = await JavaServer.async_lookup(address, timeout=QUERY_TIMEOUT)
            status = await asyncio.wait_for(server.async_status(), timeout=QUERY_TIMEOUT)
        except Exception as exc:  # timeout, DNS, connection refused, invalid response...
            log.info("Server %s unreachable: %r", address, exc)
            embed = discord.Embed(
                title="🔴 Offline",
                description=f"The server `{address}` is not responding.",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(title="🟢 Online", description=self._motd(status), color=discord.Color.green())
        embed.add_field(name="Address", value=f"`{address}`")
        embed.add_field(name="Players", value=f"{status.players.online}/{status.players.max}")
        embed.add_field(name="Version", value=status.version.name[:100])
        embed.add_field(name="Ping", value=f"{round(status.latency)} ms")

        names = [p.name for p in (status.players.sample or [])][:MAX_PLAYER_NAMES]
        if names:
            embed.add_field(name="Online now", value=", ".join(discord.utils.escape_markdown(n) for n in names), inline=False)

        # The server icon comes as a base64 image: attach it as the thumbnail.
        icon = self._icon_file(status.icon)
        if icon:
            embed.set_thumbnail(url="attachment://icon.png")
            await interaction.followup.send(embed=embed, file=icon)
        else:
            await interaction.followup.send(embed=embed)

    @staticmethod
    def _motd(status) -> str:
        """Message of the day without color codes and alignment spaces."""
        lines = (line.strip() for line in status.motd.to_plain().splitlines())
        text = "\n".join(line for line in lines if line)
        return discord.utils.escape_markdown(text)[:500] or "​"

    @staticmethod
    def _icon_file(icon: str | None) -> discord.File | None:
        if not icon or "," not in icon:
            return None
        try:
            data = base64.b64decode(icon.split(",", 1)[1])
        except ValueError:
            return None
        return discord.File(io.BytesIO(data), filename="icon.png")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Status(bot))
