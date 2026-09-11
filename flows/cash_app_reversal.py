"""Cash App Reversal — same steps as Cash App Processing."""

from __future__ import annotations

from flows.zelle_processing import run_zelle_style_flow

TEMPLATE_NAME = "Cash App Reversal"
NEEDS_BANKS = True


def run(message, send_message, bank: str, h: dict) -> None:
    run_zelle_style_flow(
        message,
        send_message,
        bank,
        h,
        template_button=TEMPLATE_NAME,
        recipient_key="cash_app_recipient",
        amount_key="cash_app_amount",
        default_recipient="Jordan",
        default_amount="$3,500.00",
    )
