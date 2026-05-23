import os
import re
import json
import time
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URL = "https://movequest.com/dashboard/hatcheries/golden"

STATE_FILE = "tier_state.json"


def send_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    requests.post(telegram_url, json=payload)


def load_previous_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def clean_number(text):
    text = text.replace(",", "").replace("K", "000")
    return float(text)


print("\n========================")
print("CHECK TIME:", datetime.utcnow())
print("========================\n")

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    print("OPENING PAGE...")

    page.goto(URL, wait_until="domcontentloaded")

    # Allow React/Web3 dashboard to fully update
    page.wait_for_timeout(30000)

    print("READING LIVE PAGE TEXT...")

    page_text = page.evaluate("document.body.innerText")

    browser.close()

print("\n========================")
print("PAGE TEXT CAPTURED")
print("========================\n")

previous_state = load_previous_state()

new_state = {}

pattern = re.findall(
    r"Tier\s+(\d)\s+Max Capacity\s+([\d,]+)\s+MQT\s+([\d.]+)\s+%\s+([\d.K]+)\s+MQT",
    page_text,
    re.MULTILINE
)

print("MATCHES FOUND:")
print(pattern)

if not pattern:
    print("NO TIER DATA FOUND")

for match in pattern:

    tier = match[0]

    current_amount = clean_number(match[1])

    percent_full = float(match[2])

    max_capacity = clean_number(match[3])

    remaining_space = round(max_capacity - current_amount, 3)

    print(
        f"Tier {tier} | "
        f"Current: {current_amount} | "
        f"Max: {max_capacity} | "
        f"Remaining: {remaining_space}"
    )

    new_state[tier] = remaining_space

    previous_remaining = previous_state.get(tier, 0)

    # Alert whenever remaining space changes and is greater than zero
    if remaining_space > 0 and remaining_space != previous_remaining:

        message = (
            f"🚨 GOLDEN HATCHERY ALERT 🚨\n\n"
            f"Tier {tier} now has space available!\n\n"
            f"Available Space: {remaining_space} MQT\n"
            f"Capacity Used: {percent_full}%\n\n"
            f"{URL}"
        )

        print("SENDING TELEGRAM ALERT...")
        send_telegram(message)

    else:
        print(f"No alert for Tier {tier}")

save_state(new_state)

print("\n========================")
print("STATE SAVED")
print("========================\n"
