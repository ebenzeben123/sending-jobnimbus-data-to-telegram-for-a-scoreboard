from flask import Flask, request
import requests
import config
import traceback
import csv
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = config.BOT_TOKEN
CHAT_ID = config.CHAT_ID
CSV_FILE = "monthly_totals.csv"

# Uppercase names of included sales reps
ALLOWED_REPS = [
    "DALTON KOTZ",
    "TYLER OBERMEIER",
    "CHAD HALEY",
    "CHRIS HANLEY",
    "MITCH KUPFENSTINER",
    "JOHN GUZMAN",
    "LUKE ALEXANDER",
    "MIKE TINDALL"
]

@app.route('/', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)

        # Only proceed if estimate is marked Approved
        if data.get("status_name", "").lower() != "approved":
            return "Skipped: Not Approved", 200

        # Extract and validate sales rep
        sales_rep = data.get("sales_rep_name", "UNKNOWN").strip().upper()
        if sales_rep not in ALLOWED_REPS:
            return "Skipped: Rep not allowed", 200

        # Extract total
        raw_total = data.get("total", 0)
        try:
            total = float(raw_total)
        except (ValueError, TypeError):
            total = 0.0

        # Get current month as string (e.g. '2025-03')
        current_month = datetime.now().strftime("%Y-%m")

        # Load or create the CSV
        totals = {}

        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rep = row["sales_rep"].strip().upper()
                    month = row.get("month", "")
                    if month == current_month:
                        totals[rep] = float(row["total"])

        # Add current sale to the running total
        totals[sales_rep] = totals.get(sales_rep, 0.0) + total

        # Save updated totals back to CSV
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["sales_rep", "total", "month"])
            writer.writeheader()
            for rep, amt in totals.items():
                writer.writerow({
                    "sales_rep": rep,
                    "total": amt,
                    "month": current_month
                })

        # Sort and format leaderboard
        sorted_totals = sorted(totals.items(), key=lambda x: x[1], reverse=True)

        def format_line(name, amount, is_top=False):
            banana = " 🍌" if is_top else ""
            return f"{name} ${amount:,.2f}{banana}"

        message = "🏆 *Monthly Sales Leaderboard:*\n\n"
        message += "\n".join(
            format_line(name, amt, is_top=(i == 0))
            for i, (name, amt) in enumerate(sorted_totals)
        )

        # Send to Telegram
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
        )

        return "OK", 200

    except Exception as e:
        error_message = f"Webhook crashed:\n{traceback.format_exc()}"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": error_message,
            }
        )
        return "Internal Server Error", 500
