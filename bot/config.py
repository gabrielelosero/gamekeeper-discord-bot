"""Bot configuration, read from environment variables (.env file)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _optional_int(name: str) -> int | None:
    """Read an optional integer: empty or missing becomes None."""
    value = os.getenv(name, "").strip()
    return int(value) if value else None


@dataclass(frozen=True)
class Config:
    token: str
    # If set, slash commands are synced to this server only:
    # during development they show up instantly instead of waiting for global propagation.
    guild_id: int | None
    welcome_channel_id: int | None
    # Welcome text: {user} becomes the member mention, {server} the server name.
    welcome_message: str
    mc_host: str
    mc_port: int


def load_config() -> Config:
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        raise SystemExit("DISCORD_TOKEN is missing: copy .env.example to .env and fill in your bot token.")

    return Config(
        token=token,
        guild_id=_optional_int("GUILD_ID"),
        welcome_channel_id=_optional_int("WELCOME_CHANNEL_ID"),
        welcome_message=os.getenv("WELCOME_MESSAGE", "").strip()
        or "Hi {user}, welcome to **{server}**! Check out the roles panel to pick your games.",
        mc_host=os.getenv("MC_HOST", "").strip(),
        mc_port=_optional_int("MC_PORT") or 25565,
    )
