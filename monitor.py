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

# Much more flexible extraction
matches = re.findall(
    r"Tier\s*(\d).*?([\d,]+)\s*MQT.*?([\d.K]+)\s*MQT",
    text,
    re.DOTALL
)

print("MATCHES FOUND:")
print(matches)

tier_limits = {
    "1": 15000,
    "2": 50000,
    "3": 100000,
    "4": 800000,
    "5": 50000
}

found_any = False

for match in matches:

    tier = match[0]
    current_str = match[1]

    try:
        current = float(current_str.replace(",", ""))
    except:
        continue

    if tier not in tier_limits:
        continue

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
