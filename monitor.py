from playwright.sync_api import sync_playwright
import requests
import re
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://movequest.com/dashboard/hatcheries/golden"

tier_limits = {
    "1": 15000,
    "2": 50000,
    "3": 100000,
    "4": 800000,
    "5": 50000
}

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(URL, timeout=120000)

    page.wait_for_timeout(10000)

    text = page.locator("body").inner_text()

    browser.close()

print("CHECKING MOVEQUEST TIERS...")
print("=" * 20)

matches = re.findall(
    r"Tier\s+(\d)\s+Max Capacity\s+([\d,]+)\s+MQT",
    text
)

print("MATCHES FOUND:")
print(matches)

found_any = False

for tier, current_str in matches:

    current = float(current_str.replace(",", ""))

    max_capacity = tier_limits[tier]

    remaining = max_capacity - current

    print("=" * 20)
    print(f"Tier {tier}")
    print(f"Current: {current}")
    print(f"Max: {max_capacity}")
    print(f"Remaining: {remaining}")

    if remaining > 0:

        found_any = True

        message = (
            f"🚨 MOVEQUEST SPACE AVAILABLE 🚨\n\n"
            f"Tier {tier}\n"
            f"Remaining Capacity: {remaining:,.4f} MQT"
        )

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": message
            }
        )

        print(f"ALERT SENT FOR TIER {tier}")

if not found_any:
    print("No tier space currently available.")
