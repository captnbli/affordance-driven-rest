import requests

BASE = "http://127.0.0.1:5000"
HEADERS = {"X-Role": "user"}  # try: user / admin

def normalize_href(href: str) -> str:
    return href.split("{", 1)[0]

def get(path: str):
    r = requests.get(BASE + path, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()

def follow(doc, rel: str):
    href = normalize_href(doc["_links"][rel]["href"])
    return get(href)

def main():
    home = get("/api")
    print("HOME:", home["api"], home["version"])

    enrolments = follow(home, "enrolments")
    print("\nENROLMENTS (collection):")
    for item in enrolments["items"]:
        print(" -", item["id"], item["status"], "->", item["_links"]["self"]["href"])

    first_href = enrolments["items"][0]["_links"]["self"]["href"]
    e = get(first_href)

    print("\nENROLMENT (detail) - raw fields only:")
    for k in ["id", "status", "studentId", "courseId", "comment"]:
        print(f"  {k}: {e.get(k)}")

    course = follow(e, "course")
    print("\nCOURSE (from enrolment via _links.course):")
    print(" ", course["id"], course["name"], "/", course["category"])

    print("\nClient 1 deliberately ignored _actions, _forms, _ui.")

if __name__ == "__main__":
    main()
