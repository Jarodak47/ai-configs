# Restore the portable AI workflow

This repository contains the global `AGENTS.md`, the Unified Process skill and the other versioned tool configurations. `codex/config.portable.toml` records a non-secret subset of Codex settings and plugin choices observed on 18 November 2026.

1. Install Codex and sign in. Clone this repository, then review the global instructions and install the skills you need.
2. Compare `codex/config.portable.toml` with the new machine's `~/.codex/config.toml` and merge only the relevant settings manually. Do not replace an existing configuration wholesale. Model and plugin availability may change.
3. Reinstall or enable the needed plugins from their available catalogs. The snapshot records choices, not installed packages, catalog credentials or connected accounts.
4. Reconnect Figma, Stitch and any other services through their official setup. The prior installation also used a local JavaScript REPL server; reinstall and configure it only if needed. Server commands, URLs, headers and credentials are intentionally excluded.
5. Reconfigure notifications, hooks, project trust, machine-specific paths and desktop preferences as needed. Review each setting on the new machine.

This snapshot does not include environment files, tokens, API keys, Codex memory contents, chats, project files or account sessions. It cannot restore those on its own. Consult the application and service documentation for current setup instructions.
