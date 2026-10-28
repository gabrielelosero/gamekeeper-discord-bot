"""Entry point: creates the bot, loads the cogs and syncs the slash commands."""

import logging

import discord
from discord.ext import commands

from bot.config import Config, load_config

# Each feature lives in its own cog inside bot/cogs/.
EXTENSIONS = [
    "bot.cogs.general",
    "bot.cogs.roles",
    "bot.cogs.welcome",
    "bot.cogs.status",
]

log = logging.getLogger("bot")


class CommunityBot(commands.Bot):
    def __init__(self, config: Config):
        intents = discord.Intents.default()
        # Required to receive on_member_join: must also be enabled in the Developer Portal
        # (Bot > Privileged Gateway Intents > Server Members Intent).
        intents.members = True
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.config = config

    async def setup_hook(self) -> None:
        for ext in EXTENSIONS:
            await self.load_extension(ext)
            log.info("Loaded %s", ext)

        if self.config.guild_id:
            guild = discord.Object(id=self.config.guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            log.info("Synced %d commands to server %s", len(synced), self.config.guild_id)
        else:
            synced = await self.tree.sync()
            log.info("Synced %d global commands", len(synced))

    async def on_ready(self) -> None:
        log.info("Logged in as %s (id %s)", self.user, self.user.id)


def main() -> None:
    config = load_config()
    discord.utils.setup_logging(level=logging.INFO)
    CommunityBot(config).run(config.token, log_handler=None)


if __name__ == "__main__":
    main()
