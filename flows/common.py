"""Shared helpers for Send-email flow modules."""

from __future__ import annotations

import re


def institution_label(bank: str) -> str:
    return re.sub(r"\s+brand(ed)?$", "", bank, flags=re.I).strip()


def branded_button_label(bank: str) -> str:
    return f"{institution_label(bank)} branded"


def button_pattern(label: str) -> re.Pattern[str]:
    return re.compile(re.escape(label).replace("'", ".?"), re.I)
