"""Courier Receipt → bank brand → text → today's date → Skip note → Send now."""

from __future__ import annotations

import re

TEMPLATE_NAME = "Courier Receipt"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    click_button = h["click_button"]
    send_text = h["send_text"]
    button_pattern = h["button_pattern"]
    branded_button_label = h["branded_button_label"]
    cfg = h["cfg"]

    click_button("📧 Send email", timeout=30_000)
    click_button(TEMPLATE_NAME, timeout=30_000)

    click_button(button_pattern(branded_button_label(bank)))
    send_text(message, send_message, cfg.get("courier_receipt_text", cfg["carrier_name"]))
    click_button(button_pattern(cfg["use_todays_date_button"]))

    click_button(re.compile(r"Skip note", re.I))
    click_button(re.compile(r"Send now", re.I))
