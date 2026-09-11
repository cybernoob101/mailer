"""Investigative Wire → beneficiary fields → routing → institution × N → Send now."""

from __future__ import annotations

import re

TEMPLATE_NAME = "Investigative Wire"
NEEDS_BANKS = True
INSTITUTION_ROUNDS = 2


def run_wire_flow(
    message,
    send_message,
    bank: str,
    h: dict,
    *,
    template_button: str | re.Pattern[str],
    institution_rounds: int,
) -> None:
    click_button = h["click_button"]
    send_text = h["send_text"]
    institution_label = h["institution_label"]
    cfg = h["cfg"]

    click_button("📧 Send email", timeout=30_000)
    click_button(template_button, timeout=30_000)

    send_text(message, send_message, cfg.get("investigative_wire_beneficiary", "Jordan Blake"))
    send_text(
        message,
        send_message,
        cfg.get("investigative_wire_address", "742 Evergreen Terrace, Springfield, IL 62704"),
    )
    send_text(message, send_message, cfg.get("investigative_wire_account", "4829173640"))
    send_text(message, send_message, cfg.get("investigative_wire_routing", "021000021"))

    institution = institution_label(bank)
    for _ in range(institution_rounds):
        click_button(re.compile(r"Custom institution", re.I))
        send_text(message, send_message, institution)

    click_button(re.compile(r"Skip note", re.I))
    click_button(re.compile(r"Send now", re.I))


def run(message, send_message, bank: str, h: dict) -> None:
    # exact match — avoid "Alias Investigative Wire"
    run_wire_flow(
        message,
        send_message,
        bank,
        h,
        template_button=re.compile(r"^Investigative Wire$"),
        institution_rounds=INSTITUTION_ROUNDS,
    )
