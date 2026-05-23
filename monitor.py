import os
import re
import time
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URL = "https://movequest.com/dashboard/hatcheries/golden"

# Prevent duplicate alerts
last_alerts = {}

def send_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    response = requests.post(telegram_url, json=payload)

    print("TELEGRAM STATUS:", response.status_code)
    print("TELEGRAM RESPONSE:", response.text)


def extract_number(value):
    value = value.replace(",", "").replace("K", "000")

    match = re.search(r"[\d.]+", value)

    if match:
        return float(match.group())

    return 0


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    print("OPENING PAGE...")

    page.goto(URL, wait_until="networkidle", timeout=120000)

    print("WAITING FOR CONTENT TO LOAD...")

    time.sleep(15)

    page_text = page.locator("body").inner_text()

    print("\n========================")
    print("PAGE TEXT LOADED")
    print("========================\n")

    print(page_text)

    matches = re.findall(
        r"Tier\s+(\d)\s+Max Capacity\s+([\d,]+)\s+MQT\s+([\d.]+)\s+%\s+([\dK]+)\s+MQT",
        page_text,
        re.DOTALL
    )

    print("\n========================")
    print("MATCHES FOUND:")
    print(matches)
    print("========================\n")

    for tier, current, percent, maximum in matches:

        current_value = extract_number(current)
        max_value = extract_number(maximum)

        remaining = round(max_value - current_value, 3)

        print(
            f"Tier {tier} | "
            f"Current: {current_value} | "
            f"Max: {max_value} | "
            f"Remaining: {remaining}"
        )

        if remaining > 0:

            previous_remaining = last_alerts.get(tier)

            if previous_remaining != remaining:

                message = (
                    f"🚨 MOVEQUEST ALERT 🚨\n\n"
                    f"Tier {tier} has space available!\n\n"
                    f"Available MQT: {remaining}"
                )

                print("\nSENDING TELEGRAM ALERT...")
                print(message)

                send_telegram(message)

                last_alerts[tier] = remaining

    print("\nCHECK COMPLETE")

    browser.close()
