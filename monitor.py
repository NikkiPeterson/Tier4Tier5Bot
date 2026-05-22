import os
import re
import time
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URL = "https://movequest.com/dashboard/hatcheries/golden"

MIN_ALERT = 0.01

def send_telegram(message):

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    requests.post(telegram_url, json=payload)

def extract_number(text):

    text = text.replace(",", "")
    text = text.replace("K", "000")

    match = re.search(r"[\d.]+", text)

    if match:
        return float(match.group())

    return 0

print("CHECKING MOVEQUEST TIERS...")

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    # Block unnecessary heavy resources
    def block_resources(route):

        if route.request.resource_type in [
            "image",
            "media",
            "font"
        ]:
            route.abort()
        else:
            route.continue_()

    page.route("**/*", block_resources)

    page.goto(
        URL,
        wait_until="networkidle",
        timeout=60000
    )

    time.sleep(8)

    page_text = page.locator("body").inner_text()

    browser.close()

print("====================")
print(page_text[:8000])

# Split text into lines
lines = page_text.splitlines()

alerts_sent = False

for i, line in enumerate(lines):

    line = line.strip()

    if "Tier" in line and "Max Capacity" in line:

        try:

            # Example:
            # Tier 4 Max Capacity

            tier_match = re.search(r"Tier\s*(\d)", line)

            if not tier_match:
                continue

            tier = tier_match.group(1)

            current_line = lines[i + 1].strip()
            percent_line = lines[i + 2].strip()
            max_line = lines[i + 3].strip()

            current_value = extract_number(current_line)
            max_value = extract_number(max_line)

            remaining = max_value - current_value

            print("====================")
            print(f"Tier {tier}")
            print(f"Current: {current_value}")
            print(f"Max: {max_value}")
            print(f"Remaining: {remaining}")

            if remaining >= MIN_ALERT:

                message = (
                    f"🚨 MOVEQUEST ALERT 🚨\n\n"
                    f"Tier {tier} has space available!\n\n"
                    f"Available Space: {remaining:.3f} MQT"
                )

                send_telegram(message)

                print(f"ALERT SENT FOR TIER {tier}")

                alerts_sent = True

        except Exception as e:

            print(f"ERROR PARSING TIER: {e}")

if not alerts_sent:

    print("No tier space currently available.")
