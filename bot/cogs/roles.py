"""Ruoli self-assign: un pannello con un pulsante per ogni ruolo."""

import re

import discord
from discord import app_commands
from discord.ext import commands


class RoleButton(discord.ui.DynamicItem[discord.ui.Button], template=r"selfrole:(?P<role_id>\d+)"):
    """Pulsante che aggiunge o toglie un ruolo a chi lo clicca.

    L'ID del ruolo è scritto nel custom_id del pulsante: così i pannelli già
    pubblicati continuano a funzionare anche dopo un riavvio, senza database.
    """

    def __init__(self, role_id: int, label: str = "Ruolo"):
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
        # Chiamato da discord.py quando qualcuno clicca un pulsante "selfrole:<id>".
        return cls(int(match["role_id"]), label=item.label or "Ruolo")

    async def callback(self, interaction: discord.Interaction) -> None:
        member = interaction.user
        role = interaction.guild.get_role(self.role_id)
        if role is None:
            await interaction.response.send_message("Questo ruolo non esiste più.", ephemeral=True)
            return

        try:
            if role in member.roles:
                await member.remove_roles(role, reason="Ruolo self-assign")
                message = f"Ruolo {role.mention} rimosso."
            else:
                await member.add_roles(role, reason="Ruolo self-assign")
                message = f"Ruolo {role.mention} assegnato."
        except discord.Forbidden:
            message = "Non ho i permessi per gestire questo ruolo: avvisa un amministratore."

        await interaction.response.send_message(message, ephemeral=True)


class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        # Registra il pulsante dinamico: riconosce i click su pannelli vecchi e nuovi.
        self.bot.add_dynamic_items(RoleButton)

    async def cog_unload(self) -> None:
        self.bot.remove_dynamic_items(RoleButton)

    @app_commands.command(name="ruoli", description="Pubblica un pannello con pulsanti per auto-assegnarsi i ruoli.")
    @app_commands.describe(
        ruolo1="Primo ruolo",
        ruolo2="Secondo ruolo (facoltativo)",
        ruolo3="Terzo ruolo (facoltativo)",
        ruolo4="Quarto ruolo (facoltativo)",
        ruolo5="Quinto ruolo (facoltativo)",
        titolo="Titolo del pannello",
    )
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.guild_only()
    async def role_panel(
        self,
        interaction: discord.Interaction,
        ruolo1: discord.Role,
        ruolo2: discord.Role | None = None,
        ruolo3: discord.Role | None = None,
        ruolo4: discord.Role | None = None,
        ruolo5: discord.Role | None = None,
        titolo: str = "Scegli i tuoi ruoli",
    ) -> None:
        # Elimina i parametri vuoti e i doppioni mantenendo l'ordine.
        roles = list(dict.fromkeys(r for r in (ruolo1, ruolo2, ruolo3, ruolo4, ruolo5) if r))

        # Il bot può gestire solo ruoli normali che stanno sotto il suo ruolo più alto.
        bot_top = interaction.guild.me.top_role
        invalid = [r for r in roles if r.is_default() or r.managed or r >= bot_top]
        if invalid:
            names = ", ".join(r.mention for r in invalid)
            await interaction.response.send_message(
                f"Non posso assegnare: {names}.\n"
                f"Nelle impostazioni del server sposta il ruolo **{bot_top.name}** sopra questi ruoli "
                "(e non usare @everyone o ruoli dei bot).",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=titolo,
            description="Clicca un pulsante per ricevere il ruolo, cliccalo di nuovo per toglierlo.\n\n"
            + "\n".join(f"• {r.mention}" for r in roles),
            color=discord.Color.blurple(),
        )
        view = discord.ui.View(timeout=None)
        for role in roles:
            view.add_item(RoleButton(role.id, label=role.name))

        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("Pannello pubblicato.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Roles(bot))
