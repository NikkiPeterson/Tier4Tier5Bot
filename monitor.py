import os
import re
import requests

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URL = "https://movequest.com/dashboard/hatcheries/golden"

# Alert if remaining space is at least this amount
MIN_ALERT = 0.01

def send_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    requests.post(telegram_url, json=payload)

def extract_number(text):
    text = text.replace(",", "").replace("K", "000")

    match = re.search(r"[\d.]+", text)

    if match:
        return float(match.group())

    return 0

print("CHECKING MOVEQUEST TIERS...")

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    URL,
    headers=headers,
    timeout=30
)

html = response.text

matches = re.findall(
    r"Tier\s*(\d)\s*Max Capacity.*?([\d,]+)\s*MQT.*?([\d.]+)\s*%.*?([\d,.K]+)\s*MQT",
    html,
    re.DOTALL | re.IGNORECASE
)

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
