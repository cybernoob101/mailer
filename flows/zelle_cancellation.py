"""Zelle Cancellation — same steps as Zelle Processing."""

from __future__ import annotations

from flows.zelle_processing import run_zelle_style_flow

TEMPLATE_NAME = "Zelle Cancellation"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    run_zelle_style_flow(
        message,
        send_message,
        bank,
        h,
        template_button=TEMPLATE_NAME,
    )
