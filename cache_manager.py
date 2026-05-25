import requests
import json
import os
import time
import jdatetime
from datetime import datetime

API_URL = "https://api.tgju.org/v1/market/indicator/summary-table-data/price_eur"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def to_jalali(miladi_str):
    dt = datetime.strptime(miladi_str[:10], "%Y/%m/%d")
    j = jdatetime.date.fromgregorian(date=dt.date())
    return j.strftime("%Y/%m/%d")

def safe_get(params):

    for i in range(5):
        try:
            r = requests.get(
                API_URL,
                params=params,
                headers=HEADERS,
                timeout=30
            )
            r.raise_for_status()
            return r.json()

        except Exception as e:
            print(f"retry {i+1}: {e}")
            time.sleep(2)

    raise Exception("API failed")

def build_new_cache(start_year=2025):

    cache = {
        "version": 1,
        "records": {
            "shamsi": {},
            "miladi": {}
        }
    }

    start = 0
    length = 30
    last_page_empty = False

    while not last_page_empty:
        try:
            data = safe_get({
                "lang": "fa",
                "start": start,
                "length": length,
                "order_dir": "desc"
            })

            rows = data.get("data", [])

            if not rows:
                break

            last_page_empty = True  # assume no progress unless we find valid rows

            for r in rows:

                price = r[3]
                miladi = r[6]
                year = int(miladi[:4])

                if year < start_year:
                    start += length
                    continue

                last_page_empty = False  # we still have relevant data

                cache["records"]["miladi"][miladi] = price
                jalali = to_jalali(miladi)
                cache["records"]["shamsi"][jalali] = price

            start += length

        except Exception as e:
            print(f"IN WHILE LOOP ERROR:\n{e}")
            break   

    return cache

def atomic_replace(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


if __name__ == "__main__":

    try :     
        with open("config.json", "r", encoding="utf-8") as f:
            cfg = json.load(f)

        cache_file = cfg["cache_file"]
        print("Building new cache...")
        new_cache = build_new_cache(cfg["start_year"])
        atomic_replace(cache_file, new_cache)
        
        print("DONE ✔")
    except Exception as e : 
        print(f"SOMETHING WENT WRONG :\n{e}")
