"""/status: stato di un server Minecraft (Java) e giocatori connessi."""

import asyncio
import base64
import io
import logging

import discord
from discord import app_commands
from discord.ext import commands
from mcstatus import JavaServer

log = logging.getLogger("bot.status")

QUERY_TIMEOUT = 5  # secondi
MAX_PLAYER_NAMES = 20


class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        config = bot.config
        # Indirizzo predefinito: "host:porta" dal file .env, se configurato.
        self.default_address = f"{config.mc_host}:{config.mc_port}" if config.mc_host else None

    @app_commands.command(name="status", description="Mostra se il server Minecraft è online e chi sta giocando.")
    @app_commands.describe(indirizzo="Indirizzo del server (es. play.esempio.it); se vuoto usa quello configurato")
    async def status(self, interaction: discord.Interaction, indirizzo: str | None = None) -> None:
        address = (indirizzo or self.default_address or "").strip()
        if not address:
            await interaction.response.send_message(
                "Nessun server configurato: imposta MC_HOST nel file .env oppure indica un indirizzo.",
                ephemeral=True,
            )
            return

        # La richiesta può richiedere qualche secondo: Discord vuole una risposta entro 3.
        await interaction.response.defer()

        try:
            server = await JavaServer.async_lookup(address, timeout=QUERY_TIMEOUT)
            status = await asyncio.wait_for(server.async_status(), timeout=QUERY_TIMEOUT)
        except Exception as exc:  # timeout, DNS, connessione rifiutata, risposta non valida...
            log.info("Server %s non raggiungibile: %r", address, exc)
            embed = discord.Embed(
                title="🔴 Offline",
                description=f"Il server `{address}` non risponde.",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(title="🟢 Online", description=self._motd(status), color=discord.Color.green())
        embed.add_field(name="Indirizzo", value=f"`{address}`")
        embed.add_field(name="Giocatori", value=f"{status.players.online}/{status.players.max}")
        embed.add_field(name="Versione", value=status.version.name[:100])
        embed.add_field(name="Ping", value=f"{round(status.latency)} ms")

        names = [p.name for p in (status.players.sample or [])][:MAX_PLAYER_NAMES]
        if names:
            embed.add_field(name="Connessi ora", value=", ".join(discord.utils.escape_markdown(n) for n in names), inline=False)

        # L'icona del server arriva come immagine base64: la alleghiamo come miniatura.
        icon = self._icon_file(status.icon)
        if icon:
            embed.set_thumbnail(url="attachment://icon.png")
            await interaction.followup.send(embed=embed, file=icon)
        else:
            await interaction.followup.send(embed=embed)

    @staticmethod
    def _motd(status) -> str:
        """Messaggio del giorno senza codici colore e spazi di allineamento."""
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
