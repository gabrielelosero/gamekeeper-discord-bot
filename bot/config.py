"""Configurazione del bot letta dalle variabili d'ambiente (file .env)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _optional_int(name: str) -> int | None:
    """Legge un intero facoltativo: vuoto o assente diventa None."""
    value = os.getenv(name, "").strip()
    return int(value) if value else None


@dataclass(frozen=True)
class Config:
    token: str
    # Se impostato, i comandi slash vengono sincronizzati solo su questo server:
    # in sviluppo compaiono subito, invece di attendere la propagazione globale.
    guild_id: int | None
    welcome_channel_id: int | None
    mc_host: str
    mc_port: int


def load_config() -> Config:
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        raise SystemExit("DISCORD_TOKEN mancante: copia .env.example in .env e inserisci il token del bot.")

    return Config(
        token=token,
        guild_id=_optional_int("GUILD_ID"),
        welcome_channel_id=_optional_int("WELCOME_CHANNEL_ID"),
        mc_host=os.getenv("MC_HOST", "").strip(),
        mc_port=_optional_int("MC_PORT") or 25565,
    )
