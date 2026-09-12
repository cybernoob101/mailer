"""Prototype Presentation → brand → attach file → Skip note → Send now."""

from __future__ import annotations

import re
from pathlib import Path

TEMPLATE_NAME = "Prototype Presentation"
NEEDS_BANKS = True


def _attach_prototype(page, file_path: Path, caption: str, pause) -> None:
    """Open Telegram attach menu, pick a file, optional caption, send."""
    # Composer attach control (label varies slightly across Telegram Web builds).
    attach = page.get_by_role("button", name=re.compile(r"Attach|Open menu|More", re.I)).last
    attach.click()
    pause()

    with page.expect_file_chooser() as fc_info:
        # Bot prefers File; Photo or Video also works.
        menu = page.get_by_role("menuitem", name=re.compile(r"^File$|Photo or Video", re.I)).first
        menu.click()
    fc_info.value.set_files(str(file_path))
    pause()

    caption_box = page.get_by_role("textbox", name=re.compile(r"caption", re.I))
    if caption and caption_box.count() > 0:
        caption_box.last.fill(caption)
        pause()

    # Icon-only send in the attach modal (no accessible "Send" name).
    send = page.locator("#portals .modal-dialog button.primary:has(i.icon-new-send)").last
    send.click(timeout=30_000)
    pause()


def run(message, send_message, bank: str, h: dict) -> None:
    click_button = h["click_button"]
    button_pattern = h["button_pattern"]
    branded_button_label = h["branded_button_label"]
    pause = h["pause"]
    cfg = h["cfg"]

    click_button("📧 Send email", timeout=30_000)
    click_button(TEMPLATE_NAME, timeout=30_000)

    click_button(button_pattern(branded_button_label(bank)))

    file_name = cfg.get("prototype_file", "assets/prototype.svg")
    file_path = Path(file_name)
    if not file_path.is_absolute():
        file_path = Path(__file__).resolve().parent.parent / file_path
    if not file_path.exists():
        raise FileNotFoundError(f"Prototype file not found: {file_path}")

    _attach_prototype(
        message.page,
        file_path,
        cfg.get("prototype_caption", "photo"),
        pause,
    )

    click_button(re.compile(r"Skip note", re.I))
    click_button(re.compile(r"Send now", re.I))
