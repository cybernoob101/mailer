"""Iron Ledger → Custom institution → type bank → Skip note → Send now."""

from __future__ import annotations

import re

TEMPLATE_NAME = "Iron Ledger"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    click_button = h["click_button"]
    send_text = h["send_text"]
    institution_label = h["institution_label"]

    click_button("📧 Send email", timeout=30_000)
    click_button(TEMPLATE_NAME, timeout=30_000)
    click_button(re.compile(r"Custom institution", re.I))

    # Codegen missed the fill; Custom institution needs an institution name.
    send_text(message, send_message, institution_label(bank))

    click_button(re.compile(r"Skip note", re.I))
    click_button(re.compile(r"Send now", re.I))
