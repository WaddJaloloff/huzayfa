from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import json, os, pytz, requests
from datetime import datetime, timezone, timedelta


app = Flask(__name__)
app.secret_key = "super_secret_key"

DATA_FILE = "data.json"
ADMIN_PASSWORD = "HUZayfa_?771"
TELEGRAM_TOKEN = "8597695048:AAH2jdv4R49BVmXd1hqHowqZyB8qiVF8A6Q"
CHAT_ID = "6565325969"


# === Fayl funksiyalari ===
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    if os.path.getsize(DATA_FILE) == 0:
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === Bosh sahifa ===
@app.route("/")
def index():
    return render_template("index.html")

# === Forma submit ===
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    phone = request.form.get("phone")
    business = request.form.get("business")
    budget = request.form.get("budget")

    if not all([name, phone, business, budget]):
        return "Barcha maydonlarni to‘ldiring!", 400

    data = load_data()
    new_id = len(data) + 1

    tz = pytz.timezone("Asia/Tashkent")
    now = datetime.now(tz)

    # JSON ga ISO formatda saqlaymiz
    iso_time = now.isoformat()

    new_entry = {
        "id": new_id,
        "name": name,
        "phone": phone,
        "business": business,
        "budget": budget,
        "status": "bog'lanmadik",
        "comment": "",
        "created_at": iso_time
    }

    data.append(new_entry)
    save_data(data)

    # Telegramga yuborish
    msg = (
        f"📩 Yangi lead keldi!\n\n"
        f"👤 Ism: {name}\n"
        f"📞 Telefon: {phone}\n"
        f"🏢 Biznes: {business}\n"
        f"💰 Budjet: {budget}\n"
    )
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        reply_markup = {
            "inline_keyboard": [
                [{"text": "📊 Dashboardni ochish", "url": "https://huzayfa.uz/dashboard"}]
            ]
        }
        payload = {
            "chat_id": CHAT_ID,
            "text": msg,
            "reply_markup": json.dumps(reply_markup)
        }
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            print("❌ Telegram xatolik:", r.text)
    except Exception as e:
        print("❌ Telegram xabar yuborilmadi:", e)

    return redirect(url_for("index"))

# === Admin login ===
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("admin.html", error="Noto‘g‘ri parol")
    return render_template("admin.html")



TASHKENT_TZ = timezone(timedelta(hours=5))

# Oyni inglizcha nomlar bilan list
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def format_datetime_manual(iso_str):
    # ISO stringni datetime ga aylantiramiz
    dt = datetime.fromisoformat(iso_str)
    # Tashkent timezone qo‘shish
    dt = dt.astimezone(TASHKENT_TZ)
    day = dt.day
    month = MONTHS[dt.month - 1]
    year = dt.year
    hour = dt.hour
    minute = dt.minute
    # 2 xonali formatlash
    return f"{day:02d} {month} {year}, {hour:02d}:{minute:02d}"




@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin"))
    
    data = load_data()
    # Eng so‘nggi lead yuqorida (ISO datetime bo‘yicha)
    data.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Admin panelda vaqtni formatlash
    for lead in data:
        lead["created_at_formatted"] = format_datetime_manual(lead["created_at"])

    
    return render_template("dashboard.html", leads=data)

@app.route("/api/leads")
def api_leads():
    data = load_data()
    data.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Har bir lead uchun formatlangan vaqt qo‘shish
    for lead in data:
        lead["created_at_formatted"] = format_datetime_manual(lead["created_at"])

    
    return jsonify(data)

# === Lead update ===
@app.route("/update/<int:lead_id>", methods=["POST"])
def update(lead_id):
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 403

    payload = request.get_json() or {}
    data = load_data()
    updated = False

    for lead in data:
        if lead["id"] == lead_id:
            if "status" in payload:
                lead["status"] = payload["status"]
            if "comment" in payload:
                lead["comment"] = payload["comment"]
            updated = True
            break

    if not updated:
        return jsonify({"error": "Lead topilmadi"}), 404

    save_data(data)
    return jsonify({"success": True})

# === Logout ===
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
