# sending-jobnimbus-data-to-telegram-for-a-scoreboard
I got sick of adding up the salesman's revenue and posting it to the group chat, so i programmed a bot to do it 

## 🛠 Telegram Bot Scorecard Automation — Overview

This project automates a **live sales leaderboard** for our roofing team using **JobNimbus webhooks**, a **Flask-based webhook listener**, and **Telegram** notifications. It tracks sales rep performance month-to-month and posts live updates to a Telegram group.

---

## 🚀 How It Works (Step-by-Step)

### 1. **Set Up the Web Server**
- Hosted a Flask app on [PythonAnywhere](https://www.pythonanywhere.com/)
- Deployed a public-facing endpoint to receive webhook events from JobNimbus.

### 2. **Webhook Flow (JobNimbus → Flask)**
- Created a webhook in JobNimbus triggered on *Estimate → Status = Approved*.
- This webhook sends JSON data to our PythonAnywhere app.

### 3. **Validate Incoming Data**
- The Flask app checks:
  - If the `status_name` is `"Approved"`
  - If the `sales_rep_name` is in our approved team list
  - If the `total` value is valid

### 4. **Track Monthly Totals**
- The server reads and writes to a CSV file called `monthly_totals.csv`
  - Structure: `sales_rep`, `total`, `month`
- Each approved estimate adds to that rep's running total for the current month.

### 5. **Build the Leaderboard**
- Sales reps are sorted by total revenue.
- The leaderboard message is formatted and sent to Telegram.
  - Example:  
    ```
    🏆 Monthly Sales Leaderboard:

    TYLER $18,200.00 🍌
    CHRIS $15,050.00
    DALTON $13,700.00
    ```

### 6. **Telegram Bot Integration**
- Uses `requests` to post the formatted message via Telegram’s Bot API.
- Credentials (bot token + chat ID) are stored in a local `bot_config.txt` or `config.py` file.

### 7. **Monthly Reset Support**
- Revenue data is stored with a `YYYY-MM` timestamp so scores auto-reset when the month changes.
- Old scores are still retained in the CSV (optional: purge logic can be added if needed).

---

## 🧠 Tech Stack

- **Python 3.11**
- **Flask** for webhook server
- **Pandas** for CSV manipulation
- **Telegram Bot API** via `requests`
- **PythonAnywhere** for hosting
- **JobNimbus** for CRM webhook integration
