"""
Automate Telegram Web (A version) → GrannyBlazerMailer bot flow.

Uses the same Chrome profile as:
  npx playwright codegen --channel=chrome --user-data-dir="$env:USERPROFILE\\chrome-playwright-profile"

Edit settings in config.json.
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


def run() -> None:
    cfg = load_config()
    profile_dir = Path.home() / cfg["profile_dir"]
    profile_dir.mkdir(parents=True, exist_ok=True)

    pause_ms = cfg["pause_ms"]
    type_delay_ms = cfg["type_delay_ms"]

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

        page.goto(cfg["telegram_url"], wait_until="domcontentloaded")

        chat_link = page.get_by_role("link", name=cfg["bot_name"]).first
        expect(chat_link).to_be_visible(timeout=60_000)
        chat_link.click()
        pause()

        message = page.get_by_role("textbox", name="Message").last
        expect(message).to_be_visible(timeout=30_000)
        type_into_message(message, "/start")
        message.press("Enter")
        pause()

        # Chat history can contain multiple copies; always use the newest.
        select_friend = page.get_by_role(
            "button", name=cfg["select_friend_button"]
        ).last
        expect(select_friend).to_be_visible(timeout=30_000)
        select_friend.click()
        pause()

        friend = page.get_by_role("button", name=cfg["friend_email"]).last
        expect(friend).to_be_visible(timeout=30_000)
        friend.click()
        pause()

        send_email = page.get_by_role("button", name="📧 Send email").last
        expect(send_email).to_be_visible(timeout=30_000)
        send_email.click()
        pause()

        # Avoid brittle #message-N ids; newest matching button in chat history.
        fdic_courier = page.get_by_role("button", name="FDIC Courier").last
        expect(fdic_courier).to_be_visible(timeout=30_000)
        fdic_courier.click()
        pause()

        send_message = page.get_by_role("button", name="Send Message").last

        # FDIC form prompts (codegen often skips these mid-steps).
        send_text(message, send_message, cfg["carrier_name"])

        use_today = page.get_by_role(
            "button", name=re.compile(re.escape(cfg["use_todays_date_button"]).replace("'", ".?"), re.I)
        ).last
        expect(use_today).to_be_visible(timeout=60_000)
        use_today.click()
        pause()

        send_text(message, send_message, cfg["vehicle_description"])
        send_text(message, send_message, cfg["vehicle_tag"])
        send_text(message, send_message, cfg["pickup_address"])
        send_text(message, send_message, cfg["pickup_instructions"])

        branded_pattern = re.escape(cfg["branded_button"]).replace("'", ".?")
        branded = page.get_by_role(
            "button", name=re.compile(branded_pattern, re.I)
        ).last
        expect(branded).to_be_visible(timeout=60_000)
        branded.click()
        pause()

        type_into_message(message, cfg["institution_name"])
        pause()

        custom_institution = page.get_by_role(
            "button", name=re.compile(r"Custom institution", re.I)
        ).last
        expect(custom_institution).to_be_visible(timeout=60_000)
        custom_institution.click()
        pause()

        send_text(message, send_message, cfg["custom_institution_name"])

        skip_note = page.get_by_role("button", name=re.compile(r"Skip note", re.I)).last
        expect(skip_note).to_be_visible(timeout=60_000)
        skip_note.click()
        pause()

        send_now = page.get_by_role("button", name=re.compile(r"Send now", re.I)).last
        expect(send_now).to_be_visible(timeout=60_000)
        send_now.click()
        pause()

        print(
            "Flow completed: /start → select friend → send email → FDIC form "
            "→ branded → custom institution → skip note → send now."
        )
        context.close()


if __name__ == "__main__":
    run()
