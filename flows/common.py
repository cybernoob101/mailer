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


def slugify(value: str, *, max_len: int = 80) -> str:
    text = value.strip()
    text = re.sub(r"[<>:\"/\\|?*\x00-\x1f]+", "", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text).strip("._")
    return (text or "step")[:max_len]


class ScreenshotRecorder:
    """Saves ui/<flow-name>/<bank>/<step>/screenshot.png after each action."""

    def __init__(self, root: Path, page) -> None:
        self.root = root
        self.page = page
        self.flow_name = "session"
        self.bank_name = "_"
        self.step_index = 0
        self.enabled = True

    def begin(self, flow_name: str, bank: str = "") -> None:
        self.flow_name = flow_name or "session"
        self.bank_name = bank or "_"
        self.step_index = 0

    def capture(self, label: str) -> Path | None:
        if not self.enabled:
            return None
        self.step_index += 1
        step = f"{self.step_index:03d}_{slugify(label)}"
        folder = self.root / slugify(self.flow_name) / slugify(self.bank_name) / step
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "screenshot.png"
        self.page.screenshot(path=str(path), full_page=False)
        return path


def attach_file_in_chat(
    page,
    file_path: Path,
    caption: str,
    pause,
    *,
    prefer_file: bool = True,
    screenshot=None,
) -> None:
    """Open Telegram attach menu, pick a file, optional caption, send via icon button."""
    attach = page.get_by_role("button", name=re.compile(r"Attach|Open menu|More", re.I)).last
    attach.click()
    pause()
    if screenshot:
        screenshot("attach_menu_open")

    menu_pat = r"^File$|Photo or Video" if prefer_file else r"Photo or Video|^File$"
    with page.expect_file_chooser() as fc_info:
        page.get_by_role("menuitem", name=re.compile(menu_pat, re.I)).first.click()
    fc_info.value.set_files(str(file_path))
    pause()
    if screenshot:
        screenshot("file_chosen")

    caption_box = page.get_by_role("textbox", name=re.compile(r"caption", re.I))
    if caption and caption_box.count() > 0:
        caption_box.last.fill(caption)
        pause()
        if screenshot:
            screenshot("caption_filled")

    page.locator("#portals .modal-dialog button.primary:has(i.icon-new-send)").last.click(
        timeout=30_000
    )
    pause()
    if screenshot:
        screenshot("attachment_sent")
