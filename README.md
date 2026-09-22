# AI Configs

Centralized AI tool configurations for all machines.

## Structure

| Tool | Path | Install |
|------|------|---------|
| AGENTS.md | `AGENTS.md` | `cp AGENTS.md ~/AGENTS.md` |
| opencode | `opencode/` | `cp -r opencode/* ~/.config/opencode/` |
| codex | `codex/` | `cp -r codex/* ~/.codex/` |
| cursor | `cursor/` | `cp -r cursor/* ~/.cursor/` |
| claude | `claude/` | Claude reads `~/AGENTS.md` directly |
| copilot | `copilot/` | `cp -r copilot/* ~/.copilot/` |

## Quick Setup

```bash
git clone https://github.com/Jarodak47/ai-configs.git ~/ai-configs

# global methodology
cp ~/ai-configs/AGENTS.md ~/AGENTS.md

# opencode
cp -r ~/ai-configs/opencode/* ~/.config/opencode/

# codex
cp -r ~/ai-configs/codex/* ~/.codex/

# cursor
cp -r ~/ai-configs/cursor/* ~/.cursor/

# copilot
cp -r ~/ai-configs/copilot/* ~/.copilot/
```

### Windows PowerShell

```powershell
git clone https://github.com/Jarodak47/ai-configs.git "$HOME\ai-configs"

# global methodology
Copy-Item "$HOME\ai-configs\AGENTS.md" "$HOME\AGENTS.md"

# opencode
New-Item -ItemType Directory -Force "$HOME\.config\opencode" | Out-Null
Copy-Item -Recurse -Force "$HOME\ai-configs\opencode\*" "$HOME\.config\opencode\"

# codex
New-Item -ItemType Directory -Force "$HOME\.codex" | Out-Null
Copy-Item -Recurse -Force "$HOME\ai-configs\codex\*" "$HOME\.codex\"

# cursor
New-Item -ItemType Directory -Force "$HOME\.cursor" | Out-Null
Copy-Item -Recurse -Force "$HOME\ai-configs\cursor\*" "$HOME\.cursor\"

# copilot
New-Item -ItemType Directory -Force "$HOME\.copilot" | Out-Null
Copy-Item -Recurse -Force "$HOME\ai-configs\copilot\*" "$HOME\.copilot\"
```

> Claude Code reads `AGENTS.md` directly from the home directory. The PowerShell commands above use `$HOME`, which resolves to the current Windows user's home directory.
