"""Unrecognized Device Login → location → device → datetime → brand → Send now."""

from __future__ import annotations

import re

TEMPLATE_NAME = "Unrecognized Device Login"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    click_button = h["click_button"]
    send_text = h["send_text"]
    button_pattern = h["button_pattern"]
    branded_button_label = h["branded_button_label"]
    cfg = h["cfg"]

    click_button("📧 Send email", timeout=30_000)
    click_button(TEMPLATE_NAME, timeout=30_000)

    send_text(
        message,
        send_message,
        cfg.get("unrecognized_device_location", "Atlanta, GA, United States"),
    )
    send_text(
        message,
        send_message,
        cfg.get("unrecognized_device_name", "Chrome on Windows"),
    )
    send_text(
        message,
        send_message,
        cfg.get("unrecognized_device_datetime", "August 26, 2026 at 2:14 PM ET"),
    )

    click_button(button_pattern(branded_button_label(bank)))
    click_button(re.compile(r"Skip note", re.I))
    click_button(re.compile(r"Send now", re.I))
