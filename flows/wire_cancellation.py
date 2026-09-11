"""Wire Cancellation — Wire Pending path + Skip note before Send now."""

from __future__ import annotations

from flows.wire_pending import run_wire_style_flow

TEMPLATE_NAME = "Wire Cancellation"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    run_wire_style_flow(
        message,
        send_message,
        bank,
        h,
        template_button=TEMPLATE_NAME,
        skip_note=True,
    )
