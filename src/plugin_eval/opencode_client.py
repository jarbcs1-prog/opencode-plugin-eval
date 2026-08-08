"""
OpenCode Model Client for plugin-eval.

Replaces Anthropic's claude_agent_sdk with OpenCode CLI subprocess calls.
Uses OpenCode's model routing (Zen API free models or local llama-server).
"""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class OpenCodeConfig:
    """Configuration for OpenCode model client."""
    opencode_bin: str = r"C:\nvm4w\nodejs\node_modules\opencode-ai\bin\opencode.exe"
    default_model: str = "opencode/nemotron-3-ultra-free"
    timeout: int = 120


class OpenCodeClient:
    """Client for invoking models through OpenCode CLI."""

    def __init__(self, config: Optional[OpenCodeConfig] = None):
        self.config = config or OpenCodeConfig()

    def _build_command(self, prompt: str, model: Optional[str] = None, system: str = "") -> list[str]:
        """Build the opencode run command."""
        cmd = [self.config.opencode_bin, "run"]
        if model:
            cmd.extend(["-m", model])
        elif self.config.default_model:
            cmd.extend(["-m", self.config.default_model])

        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        cmd.append(full_prompt)
        return cmd

    async def query(self, prompt: str, system: str = "", model: Optional[str] = None) -> dict:
        """
        Query a model through OpenCode CLI.
        Returns parsed JSON or fallback dict with raw text.
        """
        cmd = self._build_command(prompt, model, system)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.config.timeout
            )

            result_text = stdout.decode("utf-8").strip()
            stderr_text = stderr.decode("utf-8").strip()

            # Strip OpenCode's build output prefix ("> build · model-name")
            lines = result_text.split("\n")
            if lines and lines[0].startswith("> build"):
                result_text = "\n".join(lines[1:]).strip()

            # Try to parse JSON - handles raw JSON or JSON inside markdown fences
            stripped = result_text.strip()
            fence_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", stripped)
            if fence_match:
                stripped = fence_match.group(1).strip()

            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                return {"raw": result_text, "score": 0.5}

        except asyncio.TimeoutError:
            return {"raw": "", "score": 0.0, "error": "timeout"}
        except Exception as e:
            return {"raw": "", "score": 0.0, "error": str(e)}

    def query_sync(self, prompt: str, system: str = "", model: Optional[str] = None) -> dict:
        """Synchronous version for non-async contexts."""
        cmd = self._build_command(prompt, model, system)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
            )

            result_text = result.stdout.strip()
            stderr_text = result.stderr.strip()

            # Strip OpenCode's build output prefix
            lines = result_text.split("\n")
            if lines and lines[0].startswith("> build"):
                result_text = "\n".join(lines[1:]).strip()

            stripped = result_text.strip()
            fence_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", stripped)
            if fence_match:
                stripped = fence_match.group(1).strip()

            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                return {"raw": result_text, "score": 0.5}

        except subprocess.TimeoutExpired:
            return {"raw": "", "score": 0.0, "error": "timeout"}
        except Exception as e:
            return {"raw": "", "score": 0.0, "error": str(e)}


# Model aliases for the free Zen models
FREE_ZEN_MODELS = {
    "big-pickle": "opencode/big-pickle",
    "deepseek-v4-flash-free": "opencode/deepseek-v4-flash-free",
    "mimo-v2.5-free": "opencode/mimo-v2.5-free",
    "ling-3.0-flash-free": "opencode/ling-3.0-flash-free",
    "ling-3.0-tiny-free": "opencode/ling-3.0-tiny-free",
    "nemotron-3-ultra-free": "opencode/nemotron-3-ultra-free",
    "north-mini-code-free": "opencode/north-mini-code-free",
    "laguna-s-2.1-free": "opencode/laguna-s-2.1-free",
    "longcat-2.0-free": "opencode/longcat-2.0-free",
}

# Tier mapping for judge layer
TIER_TO_MODEL = {
    "haiku": "opencode/nemotron-3-ultra-free",  # Fast, free
    "sonnet": "opencode/nemotron-3-ultra-free",  # Balanced, free
    "opus": "opencode/big-pickle",  # Most capable free model
}


def _resolve_model(tier: str) -> str:
    """Map a tier name to an OpenCode model ID."""
    return TIER_TO_MODEL.get(tier, TIER_TO_MODEL["sonnet"])


# Global client instance
_client: Optional[OpenCodeClient] = None


def get_client(config: Optional[OpenCodeConfig] = None) -> OpenCodeClient:
    """Get or create the global OpenCode client."""
    global _client
    if _client is None:
        _client = OpenCodeClient(config)
    return _client


async def query_llm(prompt: str, system: str = "", model: str = "opencode/nemotron-3-ultra-free") -> dict:
    """
    Call a model via OpenCode CLI and return parsed JSON dict.
    Replaces the Anthropic SDK-based query_llm.
    """
    client = get_client()
    # If model is an Anthropic ID, map to free equivalent
    if model.startswith("claude-"):
        model = _resolve_model("sonnet")
    return await client.query(prompt, system=system, model=model)