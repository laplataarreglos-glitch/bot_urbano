import os
import requests

TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_URL = "https://bot-urbano.vercel.app/api"

if not TOKEN:
    raise ValueError("Falta la variable TELEGRAM_TOKEN")

url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
res = requests.post(url, data={"url": WEBHOOK_URL})

print(res.json())
