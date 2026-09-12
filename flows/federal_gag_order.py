"""Federal GAG Order → rep → phone → brand → custom institution → Skip note → Send now."""

from __future__ import annotations

import re

TEMPLATE_NAME = "Federal GAG Order"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    click_button = h["click_button"]
    send_text = h["send_text"]
    button_pattern = h["button_pattern"]
    branded_button_label = h["branded_button_label"]
    institution_label = h["institution_label"]
    cfg = h["cfg"]

    click_button("📧 Send email", timeout=30_000)
    click_button(TEMPLATE_NAME, timeout=30_000)

    send_text(
        message,
        send_message,
        cfg.get("federal_gag_rep", cfg.get("rep_verification_name", "Jordan Blake")),
    )
    send_text(
        message,
        send_message,
        cfg.get("federal_gag_phone", cfg.get("rep_verification_phone", "1234567890")),
    )

    click_button(button_pattern(branded_button_label(bank)))
    click_button(re.compile(r"Custom institution", re.I))
    send_text(message, send_message, institution_label(bank))

    click_button(re.compile(r"Skip note", re.I))
    click_button(re.compile(r"Send now", re.I))
