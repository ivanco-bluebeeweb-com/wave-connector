"""Connection lifecycle for Wave Connector."""
from __future__ import annotations
import json, uuid
from imperal_sdk import ActionResult
from wave_client import WaveClient
from app import chat
from schemas import (
    NoParams,
    ConnectParams, ConnectionIdParams, ConnectionList, ConnectionRecord, DeleteResult
)

_SECRET = "wave_connections"

def _mask(value: str) -> str:
    return value[:4] + "…" + value[-4:] if len(value) > 10 else "***"

async def _load_connections(ctx) -> list[dict]:
    raw = await ctx.secrets.get(_SECRET)
    if not raw: return []
    try: data = json.loads(raw)
    except: return []
    return data if isinstance(data, list) else []

async def _save_connections(ctx, conns: list[dict]) -> None:
    await ctx.secrets.set(_SECRET, json.dumps(conns))

async def resolve_connection(ctx, connection_id: str = "") -> dict | None:
    conns = await _load_connections(ctx)
    if not conns: return None
    if not connection_id:
        for c in conns:
            if c.get("is_active"):
                return c
        return conns[0]
    for c in conns:
        if c["id"] == connection_id:
            return c
    return None

@chat.function(
    "connect_wave",
    "Connect your own Wave Apps account with full-access API Token and Business ID.",
    action_type="write",
    chain_callable=True,
    event="wave-connector.connect_wave",
    effects=["create:connection"],
    data_model=ConnectParams
)
async def connect_wave(ctx, params: ConnectParams) -> ActionResult[ConnectionRecord]:
    """Connect a new account."""
    client = WaveClient(
        access_token=params.access_token,
        business_id=params.business_id,
        base_url=params.base_url
    )
    v_res = await client.verify_auth()
    if v_res.get("status") == "error":
        return ActionResult.error(
            f"Wave authentication failed: {v_res.get('message', 'Invalid credentials')}",
            code=v_res.get("code", "UNAUTHORIZED")
        )

    conns = await _load_connections(ctx)
    cid = f"conn_{uuid.uuid4().hex[:8]}"
    record = {
        "id": cid,
        "label": params.label or "Wave Account",
        "access_token": params.access_token,
        "business_id": params.business_id,
        "base_url": params.base_url or "https://gql.waveapps.com/graphql/public",
        "masked_key": _mask(params.access_token),
        "is_active": True
    }
    for c in conns:
        c["is_active"] = False
    conns.append(record)
    await _save_connections(ctx, conns)
    return ActionResult.success(ConnectionRecord(
        id=cid,
        label=record["label"],
        masked_key=record["masked_key"],
        business_id=record["business_id"],
        base_url=record["base_url"],
        is_active=True
    ))

@chat.function(
    "list_connections",
    "List connected Wave accounts without exposing sensitive tokens.",
    action_type="read",
    chain_callable=True,
    data_model=NoParams
)
async def list_connections(ctx, params: NoParams) -> ActionResult[ConnectionList]:
    """List all accounts."""
    conns = await _load_connections(ctx)
    records = [
        ConnectionRecord(
            id=c["id"],
            label=c.get("label", "Wave Account"),
            masked_key=c.get("masked_key", "***"),
            business_id=c.get("business_id", ""),
            base_url=c.get("base_url", "https://gql.waveapps.com/graphql/public"),
            is_active=c.get("is_active", False)
        )
        for c in conns
    ]
    return ActionResult.success(ConnectionList(connections=records, total=len(records)))

@chat.function(
    "disconnect_wave",
    "Disconnect a Wave account.",
    action_type="destructive",
    chain_callable=True,
    data_model=ConnectionIdParams
)
async def disconnect_wave(ctx, params: ConnectionIdParams) -> ActionResult[DeleteResult]:
    """Disconnect an account."""
    conns = await _load_connections(ctx)
    cid = params.connection_id
    if not cid:
        for c in conns:
            if c.get("is_active"):
                cid = c["id"]
                break
    conns = [c for c in conns if c["id"] != cid]
    if conns and not any(c.get("is_active") for c in conns):
        conns[0]["is_active"] = True
    await _save_connections(ctx, conns)
    return ActionResult.success(DeleteResult(id=cid or "all", deleted=True, message="Wave connection removed"))
