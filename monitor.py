import requests
import re
import os

URL = "https://movequest.com/dashboard/hatcheries/golden"

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

response = requests.get(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

text = response.text

print("CHECKING MOVEQUEST TIERS...")
print("=" * 20)

pattern = re.findall(
    r"Tier\s+(\d)\s+Max Capacity\s+([\d,]+)\s+MQT\s+([\d.]+)\s+%\s+([\d.K]+)\s+MQT",
    text,
    re.MULTILINE
)

print("MATCHES FOUND:")
print(pattern)

if not pattern:
    print(text[:5000])
    exit()

tier_limits = {
    "1": 15000,
    "2": 50000,
    "3": 100000,
    "4": 800000,
    "5": 50000
}

space_found = False

for tier, current_str, percent, max_label in pattern:

    current = float(current_str.replace(",", ""))
    max_capacity = tier_limits[tier]
    remaining = max_capacity - current

    print("=" * 20)
    print(f"Tier {tier}")
    print(f"Current: {current}")
    print(f"Max: {max_capacity}")
    print(f"Remaining: {remaining}")

    if remaining > 0:

        space_found = True

        message = (
            f"🚨 MOVEQUEST SPACE AVAILABLE 🚨\n\n"
            f"Tier {tier}\n"
            f"Remaining Capacity: {remaining:,.4f} MQT"
        )

        telegram_url = (
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        )

        requests.post(
            telegram_url,
            data={
                "chat_id": CHAT_ID,
                "text": message
            }
        )

        print(f"ALERT SENT FOR TIER {tier}")

if not space_found:
    print("No tier space currently available.")
