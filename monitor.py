import os
import re
import time
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URL = "https://movequest.com/dashboard/hatcheries/golden"

# Minimum amount of free space before alerting
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

    # Block heavy resources to speed things up
    def block_resources(route):

        resource_type = route.request.resource_type

        if resource_type in [
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
        wait_until="domcontentloaded",
        timeout=60000
    )

    time.sleep(5)

    page_text = page.locator("body").inner_text()

    browser.close()

print("====================")
print("PAGE TEXT:")
print(page_text[:5000])

matches = re.findall(
    r"Tier\s*(\d)\s*Max Capacity\s*([\d,]+)\s*MQT\s*([\d.]+)\s*%\s*([\d.K]+)\s*MQT",
    page_text,
    re.DOTALL | re.IGNORECASE
)

print("====================")
print("MATCHES FOUND:")
print(matches)

alerts_sent = False

for tier, current, percent, maximum in matches:

    current_value = extract_number(current)
    max_value = extract_number(maximum)

    remaining = max_value - current_value

    print(
        f"Tier {tier} | "
        f"Current: {current_value} | "
        f"Max: {max_value} | "
        f"Remaining: {remaining}"
    )

    if remaining >= MIN_ALERT:

        message = (
            f"🚨 MOVEQUEST ALERT 🚨\n\n"
            f"Tier {tier} has space available!\n\n"
            f"Available Space: {remaining:.3f} MQT"
        )

        send_telegram(message)

        print(f"ALERT SENT FOR TIER {tier}")

        alerts_sent = True

if not alerts_sent:
    print("No tier space currently available.")
