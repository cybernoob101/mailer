"""Wire Pending → beneficiary → amount → institution → brand header → Send now."""

from __future__ import annotations

import re

TEMPLATE_NAME = "Wire Pending"
NEEDS_BANKS = True


def run_wire_style_flow(
    message,
    send_message,
    bank: str,
    h: dict,
    *,
    template_button: str | re.Pattern[str],
    agent_name: str | None = None,
    skip_note: bool = False,
) -> None:
    """Shared wire-style path (Pending / Reversal Options / Cancellation)."""
    click_button = h["click_button"]
    send_text = h["send_text"]
    button_pattern = h["button_pattern"]
    branded_button_label = h["branded_button_label"]
    institution_label = h["institution_label"]
    cfg = h["cfg"]

    click_button("📧 Send email", timeout=30_000)
    click_button(template_button, timeout=30_000)

    send_text(
        message,
        send_message,
        cfg.get("wire_pending_beneficiary", cfg.get("investigative_wire_beneficiary", "Jordan Blake")),
    )
    send_text(message, send_message, cfg.get("wire_pending_amount", "$12,500.00"))

    click_button(re.compile(r"Custom institution", re.I))
    send_text(message, send_message, institution_label(bank))

    if agent_name is not None:
        send_text(message, send_message, agent_name)

    # Email header layout (branded), separate from receiving bank name above.
    click_button(button_pattern(branded_button_label(bank)))

    if skip_note:
        click_button(re.compile(r"Skip note", re.I))

    try:
        click_button(re.compile(r"Go to bottom", re.I), timeout=5_000)
    except Exception:
        pass

    click_button(re.compile(r"Send now", re.I))


def run(message, send_message, bank: str, h: dict) -> None:
    run_wire_style_flow(
        message,
        send_message,
        bank,
        h,
        template_button=TEMPLATE_NAME,
    )
