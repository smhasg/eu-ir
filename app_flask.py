import json
from flask import Flask, render_template, request ,jsonify 
import threading
import webbrowser
import time
import subprocess

import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def fmt(x):
    try:
        return f"{float(x):,.2f}"
    except:
        return x

app = Flask(
    __name__
    , template_folder=resource_path("templates")
)

# --------------------
# load config
# --------------------
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

CACHE_FILE = config["cache_file"]

with open(CACHE_FILE, "r", encoding="utf-8") as f:
    CACHE = json.load(f)["records"]

SHAMSI = CACHE["shamsi"]
MILADI = CACHE["miladi"]



# ---------------- flask route ----------------
@app.route("/", methods=["GET", "POST"])
    
def index():
    print("INDEX CALLED")
    result = None
    rate = None
    error = None

    shamsi_dates = list(SHAMSI.keys())
    miladi_dates = list(MILADI.keys())

    if request.method == "POST":

        mode = request.form.get("mode")
        date = request.form.get("date")
        amount_raw = request.form.get("amount", "").strip()

        if not amount_raw:
            error = "مبلغ خالی است"
            return render_template(
            "index.html",
            result=fmt(result) if result is not None else None,
            rate=fmt(rate) if rate is not None else None,
            error=error,
            dates=shamsi_dates,
            mode="shamsi"
        )

        try:
            amount = float(amount_raw)
        except:
            error = "مبلغ نامعتبر است"
            return render_template(
            "index.html",
            result=fmt(result) if result is not None else None,
            rate=fmt(rate) if rate is not None else None,
            error=error,
            dates=shamsi_dates,
            mode="shamsi"
        )
        try:

            if mode == "shamsi":
                rate = float(SHAMSI[date].replace(",", ""))
                result = amount / rate

            else:
                rate = float(MILADI[date].replace(",", ""))
                result = amount * rate

        except KeyError:
            error = "تاریخ نامعتبر انتخاب شد"
    print("BEFORE TEMPLATE")
    return render_template(
        "index.html",
        result=fmt(result) if result is not None else None,
        rate=fmt(rate) if rate is not None else None,
        error=error,
        dates=shamsi_dates,
        mode="shamsi"
    )


@app.route("/dates")
def dates():

    mode = request.args.get("mode", "shamsi")

    if mode == "miladi":
        return jsonify(list(MILADI.keys()))

    return jsonify(list(SHAMSI.keys()))

@app.route("/run-cache", methods=["POST"])
def run_cache():
    try:
        exe_path = os.path.join(os.path.dirname(__file__), "cache_manager.exe")

        subprocess.Popen(
            exe_path,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})    

# ---------------- open browser safely ----------------
def open_browser():
    time.sleep(1.5)  
    url = f"http://{config['host']}:{config['port']}"
    webbrowser.open(url)



# ---------------- main ----------------
if __name__ == "__main__":
    threading.Thread(target=open_browser).start()

    app.run(
        host=config["host"],
        port=config["port"],
        debug=False,
        use_reloader=False  
    )
    

