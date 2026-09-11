"""Send-email flow runners. Add a new module here, then import it below."""

from __future__ import annotations

from typing import Callable

from flows import (
    alias_investigative_wire,
    courier_receipt,
    evidence_shipping,
    fdic_courier,
    investigative_wire,
    iron_ledger,
    shipping_receipt,
    wire_pending,
)

_MODULES = (
    fdic_courier,
    iron_ledger,
    evidence_shipping,
    courier_receipt,
    shipping_receipt,
    investigative_wire,
    alias_investigative_wire,
    wire_pending,
)

FLOWS: dict[str, Callable] = {mod.TEMPLATE_NAME: mod.run for mod in _MODULES}
TEMPLATES_WITH_BANKS: set[str] = {
    mod.TEMPLATE_NAME for mod in _MODULES if getattr(mod, "NEEDS_BANKS", False)
}
