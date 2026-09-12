"""Prototype Presentation → brand → attach file → Skip note → Send now."""

from __future__ import annotations

import re

from flows.common import (
    attach_file_in_chat,
    branded_button_label,
    button_pattern,
    resolve_project_path,
)

TEMPLATE_NAME = "Prototype Presentation"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    click_button = h["click_button"]
    pause = h["pause"]
    cfg = h["cfg"]

    click_button("📧 Send email", timeout=30_000)
    click_button(TEMPLATE_NAME, timeout=30_000)

    click_button(button_pattern(branded_button_label(bank)))

    file_path = resolve_project_path(cfg.get("prototype_file", "assets/prototype.svg"))
    if not file_path.exists():
        raise FileNotFoundError(f"Prototype file not found: {file_path}")

    attach_file_in_chat(
        message.page,
        file_path,
        cfg.get("prototype_caption", "photo"),
        pause,
        prefer_file=True,
        screenshot=h.get("screenshot"),
    )

    click_button(re.compile(r"Skip note", re.I))
    click_button(re.compile(r"Send now", re.I))
