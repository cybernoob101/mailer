"""Investigative Wire → beneficiary fields → routing → institution → Send now."""

from __future__ import annotations

import re

TEMPLATE_NAME = "Investigative Wire"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    click_button = h["click_button"]
    send_text = h["send_text"]
    institution_label = h["institution_label"]
    cfg = h["cfg"]

    click_button("📧 Send email", timeout=30_000)
    # exact match — avoid "Alias Investigative Wire"
    click_button(re.compile(r"^Investigative Wire$"), timeout=30_000)

    send_text(message, send_message, cfg.get("investigative_wire_beneficiary", "Jordan Blake"))
    send_text(
        message,
        send_message,
        cfg.get("investigative_wire_address", "742 Evergreen Terrace, Springfield, IL 62704"),
    )
    send_text(message, send_message, cfg.get("investigative_wire_account", "4829173640"))
    send_text(message, send_message, cfg.get("investigative_wire_routing", "021000021"))

    click_button(re.compile(r"Custom institution", re.I))
    send_text(message, send_message, institution_label(bank))
    click_button(re.compile(r"Custom institution", re.I))
    send_text(message, send_message, institution_label(bank))

    click_button(re.compile(r"Skip note", re.I))
    click_button(re.compile(r"Send now", re.I))
