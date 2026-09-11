"""
Automate Telegram Web (A version) → GrannyBlazerMailer bot flow.

Uses the same Chrome profile as:
  npx playwright codegen --channel=chrome --user-data-dir="$env:USERPROFILE\\chrome-playwright-profile"

Edit:
  config.json     — emails, form field values, pauses, only_templates, bank_limit
  templates.txt   — which Send-email options to run (one per line)
  banks.txt       — banks for templates that need a brand
  flows/          — one module per Send-email template

CLI overrides config, e.g.:
  python telegram_start.py --template "Iron Ledger" --bank-limit 4
  python telegram_start.py --template "Iron Ledger" --bank-limit 4 --dry-run
  python telegram_start.py --template "Iron Ledger" --bank "Chase" --bank "USAA"

Progress is saved to progress.json as email + template + bank.
Delete progress.json (or pass --ignore-progress) to start over.

Only templates with an implemented flow module will execute; others are skipped.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

from flows import FLOWS, TEMPLATES_WITH_BANKS
from flows.common import branded_button_label, button_pattern, institution_label

CONFIG_PATH = Path(__file__).with_name("config.json")


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def load_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def friend_emails_from_config(cfg: dict) -> list[str]:
    if emails := cfg.get("friend_emails"):
        return list(emails)
    return [cfg["friend_email"]]


def progress_key(email: str, template: str, bank: str) -> str:
    return f"{email}\n{template}\n{bank}"


def load_progress(path: Path) -> set[str]:
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    completed = data.get("completed", [])
    keys: set[str] = set()
    for item in completed:
        # Migrate old progress.json entries that only had email+bank (FDIC).
        template = item.get("template", "FDIC Courier")
        bank = item.get("bank", "")
        keys.add(progress_key(item["email"], template, bank))
    return keys


def mark_completed(
    path: Path,
    email: str,
    template: str,
    bank: str,
    completed: set[str],
) -> None:
    completed.add(progress_key(email, template, bank))
    payload = {
        "completed": [
            {
                "email": email_part,
                "template": template_part,
                "bank": bank_part,
            }
            for key in sorted(completed)
            for email_part, template_part, bank_part in [key.split("\n", 2)]
        ]
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run GrannyBlazerMailer Telegram flows. CLI flags override config.json."
    )
    parser.add_argument(
        "--template",
        "-t",
        action="append",
        dest="templates",
        metavar="NAME",
        help='Only run this template (repeatable). Example: -t "Iron Ledger"',
    )
    parser.add_argument(
        "--bank-limit",
        "-n",
        type=int,
        metavar="N",
        help="Only use the first N banks from banks.txt (after only_banks filter).",
    )
    parser.add_argument(
        "--bank",
        "-b",
        action="append",
        dest="banks",
        metavar="NAME",
        help="Only use this bank name (repeatable). Must match banks.txt lines.",
    )
    parser.add_argument(
        "--email",
        "-e",
        action="append",
        dest="emails",
        metavar="NAME",
        help="Only use this friend email/name (repeatable).",
    )
    parser.add_argument(
        "--ignore-progress",
        action="store_true",
        help="Do not skip completed jobs from progress.json (still writes progress).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the job queue and exit without opening the browser.",
    )
    return parser.parse_args()


def resolve_templates(cfg: dict, args: argparse.Namespace) -> list[str]:
    templates_path = Path(__file__).with_name(cfg.get("templates_file", "templates.txt"))
    templates = load_lines(templates_path)
    if not templates:
        raise SystemExit(f"No templates found in {templates_path}")

    only = args.templates or cfg.get("only_templates")
    if only:
        wanted = set(only)
        templates = [t for t in templates if t in wanted]
        missing = wanted - set(templates)
        if missing:
            raise SystemExit(f"Unknown template(s) not in templates.txt: {sorted(missing)}")
    return templates


def resolve_banks(cfg: dict, args: argparse.Namespace) -> list[str]:
    banks_path = Path(__file__).with_name(cfg.get("banks_file", "banks.txt"))
    banks = load_lines(banks_path)

    only = args.banks or cfg.get("only_banks")
    if only:
        wanted = list(only)
        by_name = {b.casefold(): b for b in banks}
        resolved: list[str] = []
        for name in wanted:
            match = by_name.get(name.casefold())
            if not match:
                raise SystemExit(f"Bank {name!r} not found in {banks_path.name}")
            resolved.append(match)
        banks = resolved

    limit = args.bank_limit if args.bank_limit is not None else cfg.get("bank_limit")
    if limit is not None:
        banks = banks[: int(limit)]
    return banks


def resolve_emails(cfg: dict, args: argparse.Namespace) -> list[str]:
    emails = friend_emails_from_config(cfg)
    if args.emails:
        wanted = {e.casefold() for e in args.emails}
        emails = [e for e in emails if e.casefold() in wanted]
        if not emails:
            raise SystemExit(f"No friend_emails matched {args.emails!r}")
    return emails


def run(args: argparse.Namespace | None = None) -> None:
    args = args or parse_args()
    cfg = load_config()
    profile_dir = Path.home() / cfg["profile_dir"]
    profile_dir.mkdir(parents=True, exist_ok=True)

    templates = resolve_templates(cfg, args)
    banks = resolve_banks(cfg, args)
    emails = resolve_emails(cfg, args)

    banks_path = Path(__file__).with_name(cfg.get("banks_file", "banks.txt"))
    progress_path = Path(__file__).with_name(cfg.get("progress_file", "progress.json"))
    completed: set[str] = set() if args.ignore_progress else load_progress(progress_path)

    pause_ms = cfg["pause_ms"]
    type_delay_ms = cfg["type_delay_ms"]

    print(f"Templates: {templates}")
    print(f"Banks ({len(banks)}): {banks}")
    print(f"Emails: {emails}")

    # Build work queue: email × template × optional bank.
    remaining: list[tuple[str, str, str]] = []
    skipped_unimplemented: list[str] = []
    for email in emails:
        for template in templates:
            if template not in FLOWS:
                if template not in skipped_unimplemented:
                    skipped_unimplemented.append(template)
                continue
            if template in TEMPLATES_WITH_BANKS:
                if not banks:
                    raise SystemExit(
                        f"Template {template!r} needs banks, but none selected "
                        f"(check {banks_path.name}, only_banks, bank_limit)."
                    )
                for bank in banks:
                    if progress_key(email, template, bank) not in completed:
                        remaining.append((email, template, bank))
            else:
                if progress_key(email, template, "") not in completed:
                    remaining.append((email, template, ""))

    if skipped_unimplemented:
        print("Not implemented yet (add a module under flows/ when you have codegen):")
        for name in skipped_unimplemented:
            print(f"  - {name}")

    if not remaining:
        print("Nothing left to send — all implemented pairs are done, or no flows ready.")
        return

    print(f"Queue: {len(remaining)} job(s)")
    for email, template, bank in remaining:
        print(f"  - email={email!r} template={template!r} bank={bank!r}")

    if args.dry_run:
        print("Dry run only — browser not started.")
        return

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

        helpers = {
            "cfg": cfg,
            "pause": pause,
            "type_into_message": type_into_message,
            "send_text": send_text,
            "click_button": click_button,
            "button_pattern": button_pattern,
            "branded_button_label": branded_button_label,
            "institution_label": institution_label,
        }

        page.goto(cfg["telegram_url"], wait_until="domcontentloaded")

        chat_link = page.get_by_role("link", name=cfg["bot_name"]).first
        expect(chat_link).to_be_visible(timeout=60_000)
        chat_link.click()
        pause()

        message = page.get_by_role("textbox", name="Message").last
        expect(message).to_be_visible(timeout=30_000)
        send_message = page.get_by_role("button", name="Send Message").last

        current_email: str | None = None
        for email, template, bank in remaining:
            if email != current_email:
                type_into_message(message, "/start")
                message.press("Enter")
                pause()
                click_button(cfg["select_friend_button"], timeout=30_000)
                click_button(email, timeout=30_000)
                current_email = email

            print(f"Sending email={email!r} template={template!r} bank={bank!r}")
            FLOWS[template](message, send_message, bank, helpers)
            mark_completed(progress_path, email, template, bank, completed)
            print(f"Saved progress → {progress_path.name} ({len(completed)} done)")

        print("Flow completed for all remaining implemented jobs.")
        context.close()


if __name__ == "__main__":
    run()
