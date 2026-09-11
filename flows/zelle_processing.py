"""Zelle Processing → recipient → amount → brand → Skip note → Send now."""

from __future__ import annotations

import re

TEMPLATE_NAME = "Zelle Processing"
NEEDS_BANKS = True


def run_zelle_style_flow(
    message,
    send_message,
    bank: str,
    h: dict,
    *,
    template_button: str | re.Pattern[str],
    recipient_key: str = "zelle_recipient",
    amount_key: str = "zelle_amount",
    default_recipient: str = "Jordan Blade",
    default_amount: str = "$3,500.00",
) -> None:
    click_button = h["click_button"]
    send_text = h["send_text"]
    button_pattern = h["button_pattern"]
    branded_button_label = h["branded_button_label"]
    cfg = h["cfg"]

    click_button("📧 Send email", timeout=30_000)
    click_button(template_button, timeout=30_000)

    send_text(
        message,
        send_message,
        cfg.get(recipient_key, cfg.get("zelle_recipient", default_recipient)),
    )
    send_text(
        message,
        send_message,
        cfg.get(amount_key, cfg.get("zelle_amount", default_amount)),
    )

    click_button(button_pattern(branded_button_label(bank)))
    click_button(re.compile(r"Skip note", re.I))
    click_button(re.compile(r"Send now", re.I))


def run(message, send_message, bank: str, h: dict) -> None:
    run_zelle_style_flow(
        message,
        send_message,
        bank,
        h,
        template_button=TEMPLATE_NAME,
    )
