"""Evidence Shipping → custom carrier → date → default instructions → bank → Send now."""

from __future__ import annotations

import re

TEMPLATE_NAME = "Evidence Shipping"
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

    # Codegen: type carrier, then Custom carrier…
    send_text(
        message,
        send_message,
        cfg.get("evidence_carrier", cfg.get("carrier_name", "joy nate")),
    )
    click_button(re.compile(r"Custom carrier", re.I))

    send_text(
        message,
        send_message,
        cfg.get("evidence_pickup_date", "june 5, 2026"),
    )
    click_button(
        button_pattern(cfg.get("use_default_instructions_button", "Use default instructions"))
    )

    click_button(button_pattern(branded_button_label(bank)))
    click_button(re.compile(r"Custom institution", re.I))
    send_text(message, send_message, institution_label(bank))

    click_button(re.compile(r"Skip note", re.I))
    click_button(re.compile(r"Send now", re.I))
