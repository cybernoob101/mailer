"""Preliminary Evidence → brand → rep name → images → Done → Skip note → Send now."""

from __future__ import annotations

import re

from flows.common import (
    attach_file_in_chat,
    branded_button_label,
    button_pattern,
    resolve_project_path,
)

TEMPLATE_NAME = "Preliminary Evidence"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    click_button = h["click_button"]
    send_text = h["send_text"]
    pause = h["pause"]
    cfg = h["cfg"]

    click_button("📧 Send email", timeout=30_000)
    click_button(TEMPLATE_NAME, timeout=30_000)

    click_button(button_pattern(branded_button_label(bank)))
    send_text(
        message,
        send_message,
        cfg.get("preliminary_evidence_rep", "Jordan Blade"),
    )

    file_path = resolve_project_path(
        cfg.get("preliminary_evidence_file", cfg.get("prototype_file", "assets/prototype.svg"))
    )
    if not file_path.exists():
        raise FileNotFoundError(f"Evidence image not found: {file_path}")

    attach_file_in_chat(
        message.page,
        file_path,
        cfg.get("preliminary_evidence_caption", cfg.get("prototype_caption", "photo")),
        pause,
        prefer_file=True,
    )

    click_button(re.compile(r"Done.*attached|Done", re.I))
    click_button(re.compile(r"Skip note", re.I))
    click_button(re.compile(r"Send now", re.I))
