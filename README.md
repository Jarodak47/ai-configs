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
