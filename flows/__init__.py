"""Send-email flow runners. Add a new module here, then import it below."""

from __future__ import annotations

from typing import Callable

from flows import (
    courier_receipt,
    evidence_shipping,
    fdic_courier,
    iron_ledger,
    shipping_receipt,
)

_MODULES = (
    fdic_courier,
    iron_ledger,
    evidence_shipping,
    courier_receipt,
    shipping_receipt,
)

FLOWS: dict[str, Callable] = {mod.TEMPLATE_NAME: mod.run for mod in _MODULES}
TEMPLATES_WITH_BANKS: set[str] = {
    mod.TEMPLATE_NAME for mod in _MODULES if getattr(mod, "NEEDS_BANKS", False)
}
