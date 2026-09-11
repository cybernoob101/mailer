"""Alias Investigative Wire — same as Investigative Wire, institution step × 3."""

from __future__ import annotations

from flows.investigative_wire import run_wire_flow

TEMPLATE_NAME = "Alias Investigative Wire"
NEEDS_BANKS = True
INSTITUTION_ROUNDS = 3


def run(message, send_message, bank: str, h: dict) -> None:
    run_wire_flow(
        message,
        send_message,
        bank,
        h,
        template_button=TEMPLATE_NAME,
        institution_rounds=INSTITUTION_ROUNDS,
    )
