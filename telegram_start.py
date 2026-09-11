"""
Automate Telegram Web (A version) → GrannyBlazerMailer bot flow.

Uses the same Chrome profile as:
  npx playwright codegen --channel=chrome --user-data-dir="$env:USERPROFILE\\chrome-playwright-profile"

Edit settings in config.json and bank list in banks.txt.
Progress is saved to progress.json so restarts skip completed email+bank pairs.
Delete progress.json to start over.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

CONFIG_PATH = Path(__file__).with_name("config.json")


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def load_banks(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def friend_emails_from_config(cfg: dict) -> list[str]:
    if emails := cfg.get("friend_emails"):
        return list(emails)
    # Back-compat with older single-value configs.
    return [cfg["friend_email"]]


def progress_key(email: str, bank: str) -> str:
    return f"{email}\n{bank}"


def load_progress(path: Path) -> set[str]:
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    completed = data.get("completed", [])
    return {progress_key(item["email"], item["bank"]) for item in completed}


def mark_completed(path: Path, email: str, bank: str, completed: set[str]) -> None:
    completed.add(progress_key(email, bank))
    payload = {
        "completed": [
            {"email": email_part, "bank": bank_part}
            for key in sorted(completed)
            for email_part, bank_part in [key.split("\n", 1)]
        ]
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def institution_label(bank: str) -> str:
    """Bank display name used when typing the custom institution."""
    return re.sub(r"\s+brand(ed)?$", "", bank, flags=re.I).strip()


def branded_button_label(bank: str) -> str:
    """Telegram button text is '<bank> branded'."""
    base = institution_label(bank)
    return f"{base} branded"


def button_pattern(label: str) -> re.Pattern[str]:
    return re.compile(re.escape(label).replace("'", ".?"), re.I)


def run() -> None:
    cfg = load_config()
    profile_dir = Path.home() / cfg["profile_dir"]
    profile_dir.mkdir(parents=True, exist_ok=True)

    banks_path = Path(__file__).with_name(cfg.get("banks_file", "banks.txt"))
    banks = load_banks(banks_path)
    if not banks:
        raise SystemExit(f"No banks found in {banks_path}")

    progress_path = Path(__file__).with_name(cfg.get("progress_file", "progress.json"))
    completed = load_progress(progress_path)

    emails = friend_emails_from_config(cfg)
    pause_ms = cfg["pause_ms"]
    type_delay_ms = cfg["type_delay_ms"]

    remaining = [
        (email, bank)
        for email in emails
        for bank in banks
        if progress_key(email, bank) not in completed
    ]
    if not remaining:
        print("Nothing left to send — all email+bank pairs are in progress.json.")
        return

    print(f"Resuming: {len(remaining)} remaining of {len(emails) * len(banks)} total.")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            channel="chrome",
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        def pause() -> None:
            page.wait_for_timeout(pause_ms)

        def type_into_message(message, text: str) -> None:
            # Telegram Web uses a contenteditable; fill() sets value instantly and
            # often doesn't update the visible composer. Real keystrokes do.
            message.click()
            message.press("Control+a")
            message.press("Backspace")
            message.press_sequentially(text, delay=type_delay_ms)

        def send_text(message, send_message, text: str) -> None:
            expect(message).to_be_visible(timeout=30_000)
            type_into_message(message, text)
            pause()
            expect(send_message).to_be_visible(timeout=30_000)
            send_message.click()
            pause()

        def click_button(name: str | re.Pattern[str], timeout: int = 60_000) -> None:
            btn = page.get_by_role("button", name=name).last
            expect(btn).to_be_visible(timeout=timeout)
            btn.click()
            pause()

        def run_fdic_send(message, send_message, bank: str) -> None:
            click_button("📧 Send email", timeout=30_000)
            click_button("FDIC Courier", timeout=30_000)

            send_text(message, send_message, cfg["carrier_name"])
            click_button(button_pattern(cfg["use_todays_date_button"]))
            send_text(message, send_message, cfg["vehicle_description"])
            send_text(message, send_message, cfg["vehicle_tag"])
            send_text(message, send_message, cfg["pickup_address"])
            send_text(message, send_message, cfg["pickup_instructions"])

            click_button(button_pattern(branded_button_label(bank)))

            institution = institution_label(bank)
            type_into_message(message, institution)
            pause()

            click_button(re.compile(r"Custom institution", re.I))
            send_text(message, send_message, institution)

            click_button(re.compile(r"Skip note", re.I))
            click_button(re.compile(r"Send now", re.I))

        page.goto(cfg["telegram_url"], wait_until="domcontentloaded")

        chat_link = page.get_by_role("link", name=cfg["bot_name"]).first
        expect(chat_link).to_be_visible(timeout=60_000)
        chat_link.click()
        pause()

        message = page.get_by_role("textbox", name="Message").last
        expect(message).to_be_visible(timeout=30_000)
        send_message = page.get_by_role("button", name="Send Message").last

        current_email: str | None = None
        for email, bank in remaining:
            if email != current_email:
                type_into_message(message, "/start")
                message.press("Enter")
                pause()

                click_button(cfg["select_friend_button"], timeout=30_000)
                click_button(email, timeout=30_000)
                current_email = email

            print(f"Sending for email={email!r} bank={bank!r}")
            run_fdic_send(message, send_message, bank)
            mark_completed(progress_path, email, bank, completed)
            print(f"Saved progress → {progress_path.name} ({len(completed)} done)")

        print(
            f"Flow completed: {len(emails)} email(s) × {len(banks)} bank(s) "
            f"= {len(emails) * len(banks)} send(s)."
        )
        context.close()


if __name__ == "__main__":
    run()
