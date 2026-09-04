"""Extension declaration, capabilities, health check for Wave Connector."""
from __future__ import annotations
import json
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "wave-connector",
    version="0.1.0",
    display_name="Wave",
    icon="icon.svg",
    capabilities=["wave:manage"],
    description="Official Imperal connector for Wave (C27. Accounting & Bookkeeping). Manage operations securely."
)

chat = ChatExtension(ext)

@ext.health_check
async def health_check(ctx) -> dict:
    raw = await ctx.secrets.get("wave_connections")
    try:
        count = len(json.loads(raw)) if raw else 0
    except Exception:
        count = 0
    return {
        "healthy": True,
        "detail": f"{count} Wave connection(s) configured." if count else "Not connected yet."
    }
