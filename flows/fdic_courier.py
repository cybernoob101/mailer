"""FDIC Courier → form fields → bank brand → custom institution → Send now."""

from __future__ import annotations

import re

TEMPLATE_NAME = "FDIC Courier"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    click_button = h["click_button"]
    send_text = h["send_text"]
    type_into_message = h["type_into_message"]
    pause = h["pause"]
    cfg = h["cfg"]
    button_pattern = h["button_pattern"]
    branded_button_label = h["branded_button_label"]
    institution_label = h["institution_label"]

    click_button("📧 Send email", timeout=30_000)
    click_button(TEMPLATE_NAME, timeout=30_000)

    send_text(message, send_message, cfg["carrier_name"])
    click_button(button_pattern(cfg["use_todays_date_button"]))
    send_text(message, send_message, cfg["vehicle_description"])
    send_text(message, send_message, cfg["vehicle_tag"])
    send_text(message, send_message, cfg["pickup_address"])
    send_text(message, send_message, cfg["pickup_instructions"])

    click_button(button_pattern(branded_button_label(bank)))

    institution = institution_label(bank)
    type_into_message(message, institution)
    pause()

    click_button(re.compile(r"Custom institution", re.I))
    send_text(message, send_message, institution)

    click_button(re.compile(r"Skip note", re.I))
    click_button(re.compile(r"Send now", re.I))
