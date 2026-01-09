import requests

BASE = "http://127.0.0.1:5000"
HEADERS = {"X-Role": "user"}  # try admin

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
    first_href = enrolments["items"][0]["_links"]["self"]["href"]
    e = get(first_href)

    print("ENROLMENT:", e["id"], e["status"])
    print("\nACTIONS:")
    for name, a in e["_actions"].items():
        print(name, "enabled=", a["enabled"])

    submit = e["_actions"]["submit"]
    if submit["enabled"]:
        payload = {"confirm": True, "comment": "Submitted by client2"}
        e2 = req(submit["method"], submit["href"], json=payload)
        print("SUBMITTED:", e2["status"])

if __name__ == "__main__":
    main()
