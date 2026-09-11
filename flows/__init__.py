"""Send-email flow runners. Add a new module here, then import it below."""

from __future__ import annotations

from typing import Callable

from flows import (
    alias_investigative_wire,
    cash_app_cancellation,
    cash_app_processing,
    cash_app_reversal,
    courier_receipt,
    evidence_shipping,
    fdic_courier,
    in_branch_appointment,
    in_branch_withdrawal,
    investigative_wire,
    iron_ledger,
    shipping_receipt,
    wire_pending,
    wire_reversal_options,
    zelle_cancellation,
    zelle_processing,
    zelle_reversal,
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
    wire_reversal_options,
    zelle_processing,
    zelle_cancellation,
    zelle_reversal,
    cash_app_processing,
    cash_app_cancellation,
    cash_app_reversal,
    in_branch_withdrawal,
    in_branch_appointment,
)

FLOWS: dict[str, Callable] = {mod.TEMPLATE_NAME: mod.run for mod in _MODULES}
TEMPLATES_WITH_BANKS: set[str] = {
    mod.TEMPLATE_NAME for mod in _MODULES if getattr(mod, "NEEDS_BANKS", False)
}
