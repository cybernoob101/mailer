"""Shared helpers for Send-email flow modules."""

from __future__ import annotations

import re
from pathlib import Path


def institution_label(bank: str) -> str:
    return re.sub(r"\s+brand(ed)?$", "", bank, flags=re.I).strip()


def branded_button_label(bank: str) -> str:
    return f"{institution_label(bank)} branded"


def button_pattern(label: str) -> re.Pattern[str]:
    return re.compile(re.escape(label).replace("'", ".?"), re.I)


def resolve_project_path(relative_or_absolute: str) -> Path:
    path = Path(relative_or_absolute)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent.parent / path
    return path


def attach_file_in_chat(page, file_path: Path, caption: str, pause, *, prefer_file: bool = True) -> None:
    """Open Telegram attach menu, pick a file, optional caption, send via icon button."""
    attach = page.get_by_role("button", name=re.compile(r"Attach|Open menu|More", re.I)).last
    attach.click()
    pause()

    menu_pat = r"^File$|Photo or Video" if prefer_file else r"Photo or Video|^File$"
    with page.expect_file_chooser() as fc_info:
        page.get_by_role("menuitem", name=re.compile(menu_pat, re.I)).first.click()
    fc_info.value.set_files(str(file_path))
    pause()

    caption_box = page.get_by_role("textbox", name=re.compile(r"caption", re.I))
    if caption and caption_box.count() > 0:
        caption_box.last.fill(caption)
        pause()

    # Icon-only send in the attach modal (no accessible "Send" name).
    page.locator("#portals .modal-dialog button.primary:has(i.icon-new-send)").last.click(
        timeout=30_000
    )
    pause()
