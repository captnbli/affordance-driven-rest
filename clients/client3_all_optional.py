import requests
from collections import defaultdict

BASE = "http://127.0.0.1:5000"
HEADERS = {"X-Role": "user"}

def normalize_href(href: str) -> str:
    return href.split("{", 1)[0]

def req(method: str, path: str, json=None):
    r = requests.request(method, BASE + path, headers=HEADERS, json=json, timeout=10)
    if r.status_code >= 400:
        print("ERROR:", r.text)
        r.raise_for_status()
    return r.json()

def get(path: str):
    return req("GET", path)

def main():
    home = get("/api")
    enrolments = get(normalize_href(home["_links"]["enrolments"]["href"]))
    e = get(enrolments["items"][0]["_links"]["self"]["href"])

    print(e["_ui"]["title"])
    print("Badges:", [b["text"] for b in e["_ui"]["badges"]])

    upd = e["_actions"]["update"]
    if upd["enabled"]:
        fields = e["_forms"]["update"]["fields"]
        payload = {}
        for f in fields:
            ui = f.get("ui", {})
            if ui.get("control") == "choice":
                src = ui["source"]
                courses = get(src["href"] + "?sort=" + ",".join(src.get("sort", [])))
                payload[f["name"]] = courses["items"][0][src["valueField"]]
            elif f["name"] == "comment":
                payload[f["name"]] = "Updated by client3"
        e = req("PATCH", upd["href"], json=payload)
        print("UPDATED courseId:", e["courseId"])

    sub = e["_actions"]["submit"]
    if sub["enabled"]:
        payload = {"confirm": True, "comment": "Submitted by client3"}
        e2 = req("POST", sub["href"], json=payload)
        print("SUBMITTED:", e2["status"])

if __name__ == "__main__":
    main()
