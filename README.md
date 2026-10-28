# Bot Discord per community di gioco

Bot di esempio per server Discord di community di gioco: comandi slash, ruoli con pulsanti,
messaggio di benvenuto e stato di un server Minecraft. Scritto in Python con
[discord.py](https://github.com/Rapptz/discord.py), si avvia con un solo comando grazie a Docker.

| Ruoli con pulsanti | Benvenuto ai nuovi membri |
|---|---|
| ![Pannello ruoli con pulsanti](docs/screenshots/ruoli.png) | ![Messaggio di benvenuto](docs/screenshots/benvenuto.png) |

| Stato di un server Minecraft | Informazioni sul bot |
|---|---|
| ![/status con server online e offline](docs/screenshots/status.png) | ![/info](docs/screenshots/info.png) |

## Funzionalità

| Comando / evento | Cosa fa | Chi può usarlo |
|---|---|---|
| `/ping` | Risponde con la latenza del bot | Tutti |
| `/info` | Nome, server, uptime e latenza del bot | Tutti |
| `/ruoli` | Pubblica un pannello con un pulsante per ogni ruolo (fino a 5): chi clicca riceve il ruolo, chi riclicca lo toglie | Chi può gestire i ruoli |
| Nuovo membro | Messaggio di benvenuto con avatar nel canale configurato | Automatico |
| `/benvenuto-prova` | Invia il benvenuto per te, per vedere come appare | Chi può gestire il server |
| `/status [indirizzo]` | Stato di un server Minecraft Java: online/offline, giocatori, versione, ping, icona | Tutti |

I pulsanti dei ruoli continuano a funzionare anche dopo un riavvio del bot, senza database:
l'ID del ruolo è salvato nel pulsante stesso.

## 1. Creare il bot nel Developer Portal

1. Vai su <https://discord.com/developers/applications> e clicca **New Application**.
2. Nella pagina **Bot**:
   - clicca **Reset Token** e copia il token (è una password: non condividerlo);
   - in *Privileged Gateway Intents* attiva **Server Members Intent** (serve per il benvenuto);
   - lascia **spento** *Requires OAuth2 Code Grant*.
3. Nella pagina **OAuth2 → URL Generator** seleziona gli scope `bot` e `applications.commands`
   e i permessi *View Channels*, *Send Messages*, *Embed Links*, *Manage Roles*.
   Apri il link generato e invita il bot nel tuo server.
4. Nelle impostazioni del server, in **Ruoli**, trascina il ruolo del bot **sopra** i ruoli che
   dovrà assegnare: Discord permette a un bot di gestire solo i ruoli sotto il suo.

## 2. Configurazione

```bash
cp .env.example .env
```

| Variabile | Obbligatoria | Descrizione |
|---|---|---|
| `DISCORD_TOKEN` | Sì | Token del bot |
| `GUILD_ID` | No | ID del server: i comandi compaiono subito lì invece che dopo la propagazione globale |
| `WELCOME_CHANNEL_ID` | No | ID del canale per il benvenuto |
| `WELCOME_MESSAGE` | No | Testo del benvenuto; `{user}` = menzione del membro, `{server}` = nome del server |
| `MC_HOST` / `MC_PORT` | No | Server Minecraft predefinito per `/status` (porta predefinita 25565) |

Per copiare gli ID attiva in Discord *Impostazioni → Avanzate → Modalità sviluppatore*,
poi tasto destro su server o canale → **Copia ID**.

## 3. Avvio

### Con Docker (consigliato)

```bash
docker compose up -d --build   # costruisce l'immagine e avvia il bot in background
docker compose logs -f         # log in tempo reale
docker compose down            # ferma il bot
```

Il container si riavvia da solo in caso di errore o di riavvio della macchina
(`restart: unless-stopped`) e gira con un utente senza privilegi.

### Senza Docker

Serve Python 3.11 o successivo.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m bot.main
```

## Struttura

```
bot/
├── main.py          # avvio, caricamento dei moduli, sincronizzazione comandi
├── config.py        # lettura delle impostazioni da .env
└── cogs/            # un modulo per funzionalità
    ├── general.py   # /ping, /info
    ├── roles.py     # /ruoli e pulsanti
    ├── welcome.py   # benvenuto e /benvenuto-prova
    └── status.py    # /status Minecraft
```

Per aggiungere una funzionalità basta creare un nuovo file in `bot/cogs/` e aggiungerlo
alla lista `EXTENSIONS` in `bot/main.py`.

## Sicurezza

Il file `.env` è escluso da git e dall'immagine Docker: il token non finisce mai nel
repository. Se un token viene esposto, rigeneralo subito con **Reset Token**.
