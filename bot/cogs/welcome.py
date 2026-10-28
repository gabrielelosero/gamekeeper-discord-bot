"""Messaggio di benvenuto automatico per i nuovi membri."""

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
        embed = discord.Embed(title=f"Benvenuto, {member.display_name}!", description=text, color=discord.Color.green())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Sei il membro numero {member.guild.member_count}")
        return embed

    async def send_welcome(self, member: discord.Member) -> bool:
        """Invia il benvenuto nel canale configurato. Restituisce False se non è possibile."""
        channel = member.guild.get_channel(self.channel_id) if self.channel_id else None
        if not isinstance(channel, discord.TextChannel):
            log.warning("Canale di benvenuto non configurato o non trovato (WELCOME_CHANNEL_ID=%s)", self.channel_id)
            return False

        try:
            # La menzione nel testo fa arrivare la notifica al nuovo membro.
            await channel.send(content=member.mention, embed=self.build_embed(member))
        except discord.Forbidden:
            log.warning("Permessi insufficienti per scrivere in #%s", channel.name)
            return False
        return True

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if not member.bot:
            await self.send_welcome(member)

    @app_commands.command(name="benvenuto-prova", description="Invia il messaggio di benvenuto per te, per vedere come appare.")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def welcome_test(self, interaction: discord.Interaction) -> None:
        if await self.send_welcome(interaction.user):
            await interaction.response.send_message(f"Inviato in <#{self.channel_id}>.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "Non riesco a inviare il benvenuto: controlla WELCOME_CHANNEL_ID nel file .env "
                "e che il bot possa scrivere in quel canale.",
                ephemeral=True,
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Welcome(bot))
