"""In-Branch Withdrawal → branch address → amount → brand → Skip note → Send now."""

from __future__ import annotations

from flows.zelle_processing import run_zelle_style_flow

TEMPLATE_NAME = "In-Branch Withdrawal"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    run_zelle_style_flow(
        message,
        send_message,
        bank,
        h,
        template_button=TEMPLATE_NAME,
        recipient_key="in_branch_address",
        amount_key="in_branch_amount",
        default_recipient="420 Montgomery St, San Francisco, CA 94104",
        default_amount="$8,500.00",
    )
