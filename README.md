# opencode-plugin-eval

Three-layer quality evaluation framework for OpenCode skills and plugins.

> **Disclaimer:** This plugin is not built by the OpenCode team and is not affiliated with OpenCode in any way. It is an independent community project.

## Installation

### From GitHub (recommended)
```bash
pip install git+https://github.com/jarbcs1-prog/opencode-plugin-eval.git
```

### From source
```bash
git clone https://github.com/jarbcs1-prog/opencode-plugin-eval.git
cd opencode-plugin-eval
pip install -e .
```

### Development install with LLM judge support
```bash
pip install -e "git+https://github.com/jarbcs1-prog/opencode-plugin-eval.git#egg=plugin-eval[llm]"
```

Or from source:
```bash
git clone https://github.com/jarbcs1-prog/opencode-plugin-eval.git
cd opencode-plugin-eval
pip install -e ".[llm]"
```

## Quick Start

```bash
# Evaluate a skill (static only, instant)
plugin-eval score path/to/skill --depth quick

# Evaluate with LLM judge (~30s)
plugin-eval score path/to/skill --depth standard

# Full certification (all layers, ~2-5 min)
plugin-eval certify path/to/skill

# Head-to-head comparison
plugin-eval compare path/to/skill-a path/to/skill-b

# Initialize corpus for Elo ranking
plugin-eval init path/to/plugins
```

## OpenCode Commands

After installing, use these commands directly in OpenCode:

| CLI | OpenCode | Description |
| --- | -------- | ----------- |
| `plugin-eval score` | `/eval` | Score a plugin or skill |
| `plugin-eval certify` | `/certify` | Full certification with badge |
| `plugin-eval compare` | `/compare` | Head-to-head comparison |
| `plugin-eval init` | — | Build corpus for Elo ranking |

## Layers

1. **Static Analysis** — Structural checks, anti-pattern detection. Instant, free.
2. **LLM Judge** — Semantic evaluation (triggering, orchestration, output, scope). ~30s, 4 calls.
3. **Monte Carlo** — Statistical reliability via 50–100 simulated runs. ~2–5 min.

## Documentation

See **[docs/plugin-eval.md](../../docs/plugin-eval.md)** for the full reference: layers, dimensions, scoring formula, anti-patterns, statistical methods and project structure.