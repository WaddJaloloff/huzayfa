from flask import Flask, render_template, request, redirect, url_for, session
import json, os, datetime, requests

app = Flask(__name__)
app.secret_key = "super_secret_key"  # session uchun

DATA_FILE = "data.json"
ADMIN_PASSWORD = "HUZayfa_?771"  # <-- admin parol
TELEGRAM_TOKEN = "8597695048:AAH2jdv4R49BVmXd1hqHowqZyB8qiVF8A6Q"  # <-- o'zingizniki bilan almashtiring
CHAT_ID = "6565325969"           # <-- chat_id yoki user_id

# === Fayl funksiyalari ===
def load_data():
    # Agar fayl mavjud bo‘lmasa — yaratamiz
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

    # Fayl bo‘sh bo‘lsa — [] qaytaramiz
    if os.path.getsize(DATA_FILE) == 0:
        return []

    # JSONni o‘qish
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []  # buzilgan fayl bo‘lsa ham bo‘sh ro‘yxat qaytaradi


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === Bosh sahifa (forma bilan) ===
@app.route("/")
def index():
    return render_template("index.html")

# === Forma ma'lumotlarini qabul qilish ===
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
    new_entry = {
        "id": new_id,
        "name": name,
        "phone": phone,
        "business": business,
        "budget": budget,
        "status": "bog'lanmadik",
        "comment": "",
        "created_at": datetime.datetime.now().isoformat()
    }
    data.append(new_entry)
    save_data(data)

    # === Telegramga habar yuborish ===
    msg = (
        f"📩 Yangi lead keldi!\n\n"
        f"👤 Ism: {name}\n"
        f"📞 Telefon: {phone}\n"
        f"🏢 Biznes: {business}\n"
        f"💰 Budjet: {budget}\n"
        f"🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.get(url, params={"chat_id": CHAT_ID, "text": msg})
        if r.status_code != 200:
            print("❌ Telegram xatolik:", r.text)
    except Exception as e:
        print("❌ Telegram xabar yuborilmadi:", e)

    # 🔥 ShU joyda RETURN kerak:
    return redirect(url_for("index"))


# === Admin login sahifasi ===
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

# === Admin panel (jadval bilan) ===
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin"))
    data = sorted(load_data(), key=lambda x: x["created_at"], reverse=True)
    return render_template("dashboard.html", leads=data)

@app.route("/update/<int:lead_id>", methods=["POST"])
def update(lead_id):
    if not session.get("admin"):
        return {"error": "Unauthorized"}, 403

    payload = request.get_json()
    data = load_data()

    for lead in data:
        if lead["id"] == lead_id:
            if "status" in payload:
                lead["status"] = payload["status"]
            if "comment" in payload:
                lead["comment"] = payload["comment"]
            break

    save_data(data)
    return {"success": True}


@app.route("/api/leads")
def api_leads():
    if not session.get("admin"):
        return {"error": "Unauthorized"}, 403
    data = sorted(load_data(), key=lambda x: x["created_at"], reverse=True)
    return data




# === Admin chiqish ===
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
