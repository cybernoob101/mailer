"""Temporary Password → password → brand → Skip note → Send now."""

from __future__ import annotations

import re

TEMPLATE_NAME = "Temporary Password"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    click_button = h["click_button"]
    send_text = h["send_text"]
    button_pattern = h["button_pattern"]
    branded_button_label = h["branded_button_label"]
    cfg = h["cfg"]

    click_button("📧 Send email", timeout=30_000)
    click_button(TEMPLATE_NAME, timeout=30_000)

    send_text(message, send_message, cfg.get("temporary_password", "tem_password"))
    click_button(button_pattern(branded_button_label(bank)))
    click_button(re.compile(r"Skip note", re.I))
    click_button(re.compile(r"Send now", re.I))
