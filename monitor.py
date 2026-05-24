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

# Print first chunk for debugging
print(text[:15000])

# Exact structure from live page text
pattern = re.findall(
    r"Tier\s+(\d)\s+Max Capacity\s+([\d,]+)\s+MQT",
    text
)

print("MATCHES FOUND:")
print(pattern)

tier_limits = {
    "1": 15000,
    "2": 50000,
    "3": 100000,
    "4": 800000,
    "5": 50000
}

found_any = False

for tier, current_str in pattern:

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

        result = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": message
            }
        )

        print(result.text)
        print(f"ALERT SENT FOR TIER {tier}")

if not found_any:
    print("No tier space currently available.")
