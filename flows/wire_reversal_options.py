"""Wire Reversal Options — Wire Pending + assigned agent name before branding."""

from __future__ import annotations

from flows.wire_pending import run_wire_style_flow

TEMPLATE_NAME = "Wire Reversal Options"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    cfg = h["cfg"]
    run_wire_style_flow(
        message,
        send_message,
        bank,
        h,
        template_button=TEMPLATE_NAME,
        agent_name=cfg.get("wire_reversal_agent", "Helen Peter"),
    )
