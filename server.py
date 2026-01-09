from __future__ import annotations

from dataclasses import dataclass, asdict
from flask import Flask, jsonify, request, abort
from typing import Dict, Any, List, Optional

app = Flask(__name__)

# -------------------------
# In-memory "domain"
# -------------------------

@dataclass
class Enrolment:
    id: str
    status: str  # DRAFT | SUBMITTED
    studentId: str
    courseId: str
    comment: str = ""

COURSES = [
    {"id": "c_1", "name": "Carpentry 101", "category": "Trades"},
    {"id": "c_2", "name": "Plumbing Basics", "category": "Trades"},
    {"id": "c_3", "name": "Intro to Python", "category": "IT"},
    {"id": "c_4", "name": "Networks 1", "category": "IT"},
]

ENROLMENTS: Dict[str, Enrolment] = {
    "enr_123": Enrolment(id="enr_123", status="DRAFT", studentId="stu_9", courseId="c_3"),
    "enr_124": Enrolment(id="enr_124", status="SUBMITTED", studentId="stu_9", courseId="c_1", comment="Submitted earlier"),
}

# -------------------------
# Helpers
# -------------------------

def role() -> str:
    # For demo: caller passes X-Role header: user|admin
    return request.headers.get("X-Role", "user").lower()

def can_submit(e: Enrolment) -> bool:
    return e.status == "DRAFT" and role() in ("user", "admin")

def can_cancel(e: Enrolment) -> bool:
    return e.status == "DRAFT" and role() == "admin"

def can_edit(e: Enrolment) -> bool:
    return e.status == "DRAFT" and role() in ("user", "admin")

def link(href: str, method: Optional[str] = None, templated: bool = False) -> Dict[str, Any]:
    obj: Dict[str, Any] = {"href": href}
    if method:
        obj["method"] = method
    if templated:
        obj["templated"] = True
    return obj

def enrolment_rep(e: Enrolment) -> Dict[str, Any]:
    # Core representation
    rep: Dict[str, Any] = asdict(e)

    # Navigational links (used by all clients)
    rep["_links"] = {
        "self": link(f"/enrolments/{e.id}"),
        "collection": link("/enrolments"),
        "home": link("/api"),
        "course": link(f"/courses/{e.courseId}"),
        "courses": link("/courses{?q,sort}", templated=True),
    }

    # Actions (optional)
    rep["_actions"] = {
        "submit": {
            "href": f"/enrolments/{e.id}/submit",
            "method": "POST",
            "enabled": can_submit(e),
            **({} if can_submit(e) else {"disabledReason": "Only DRAFT enrolments can be submitted (and you must be permitted)."}),
        },
        "cancel": {
            "href": f"/enrolments/{e.id}/cancel",
            "method": "POST",
            "enabled": can_cancel(e),
            **({} if can_cancel(e) else {"disabledReason": "Only admins can cancel DRAFT enrolments."}),
        },
        "update": {
            "href": f"/enrolments/{e.id}",
            "method": "PATCH",
            "enabled": can_edit(e),
            **({} if can_edit(e) else {"disabledReason": "Cannot edit after submission."}),
        },
    }

    # Forms for actions (optional)
    rep["_forms"] = {
        "submit": {
            "fields": [
                {
                    "name": "confirm",
                    "type": "boolean",
                    "required": True,
                    "ui": {
                        "control": "boolean",
                        "label": "I confirm this enrolment is complete",
                    },
                },
                {
                    "name": "comment",
                    "type": "string",
                    "required": False,
                    "ui": {
                        "control": "textarea",
                        "label": "Comment",
                        "rows": 3,
                        "cols": 50,
                        "placeholder": "Optional comment (visible to staff)",
                    },
                },
            ]
        },
        "update": {
            "fields": [
                {
                    "name": "courseId",
                    "type": "string",
                    "required": True,
                    "ui": {
                        "control": "choice",
                        "label": "Course",
                        "source": {
                            "href": "/courses",
                            "valueField": "id",
                            "labelField": "name",
                            "groupBy": "category",
                            "sort": ["category", "name"],
                        },
                    },
                },
                {
                    "name": "comment",
                    "type": "string",
                    "required": False,
                    "ui": {
                        "control": "text",
                        "label": "Comment",
                        "placeholder": "Short note",
                    },
                },
            ]
        },
    }

    # Read-only UI hints (optional)
    rep["_ui"] = {
        "title": f"Enrolment {e.id}",
        "badges": [{"text": e.status}],
        "fieldOrder": ["id", "status", "studentId", "courseId", "comment"],
    }

    return rep

def error(code: str, message: str, details: Optional[List[Dict[str, Any]]] = None, http_status: int = 400):
    payload: Dict[str, Any] = {"error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return jsonify(payload), http_status

# -------------------------
# Routes
# -------------------------

@app.get("/api")
def home():
    links = {
        "self": link("/api"),
        "me": link("/me"),
        "enrolments": link("/enrolments{?status,limit,offset}", templated=True),
        "courses": link("/courses{?q,sort}", templated=True),
    }
    return jsonify({"api": "affordance-demo", "version": "v1", "_links": links})

@app.get("/me")
def me():
    return jsonify({"role": role(), "_links": {"self": link("/me"), "home": link("/api")}})

@app.get("/courses")
def courses():
    q = (request.args.get("q") or "").lower().strip()
    sort = (request.args.get("sort") or "name").strip()

    items = [c for c in COURSES if (q in c["name"].lower() or q in c["category"].lower())] if q else list(COURSES)

    sort_keys = [s.strip() for s in sort.split(",") if s.strip()]

    def sort_key(c):
        return tuple(c.get(k, "") for k in sort_keys)

    items.sort(key=sort_key)

    self_href = "/courses"
    if sort_keys:
        self_href = f"/courses?sort={','.join(sort_keys)}"
    if q:
        self_href += ("&" if "?" in self_href else "?") + f"q={q}"

    return jsonify({
        "items": items,
        "_links": {
            "self": link(self_href),
            "home": link("/api"),
        }
    })

@app.get("/courses/<course_id>")
def course_by_id(course_id: str):
    c = next((c for c in COURSES if c["id"] == course_id), None)
    if not c:
        abort(404)
    return jsonify({
        **c,
        "_links": {"self": link(f"/courses/{course_id}"), "collection": link("/courses"), "home": link("/api")}
    })

@app.get("/enrolments")
def enrolments():
    status = (request.args.get("status") or "").strip().upper()
    limit = int(request.args.get("limit") or 50)
    offset = int(request.args.get("offset") or 0)

    items = list(ENROLMENTS.values())
    if status:
        items = [e for e in items if e.status == status]

    page = items[offset: offset + limit]

    rep_items = []
    for e in page:
        rep_items.append({
            "id": e.id,
            "status": e.status,
            "studentId": e.studentId,
            "_links": {"self": link(f"/enrolments/{e.id}")},
        })

    links = {
        "self": link(f"/enrolments?limit={limit}&offset={offset}" + (f"&status={status}" if status else "")),
        "home": link("/api"),
    }
    if offset + limit < len(items):
        links["next"] = link(f"/enrolments?limit={limit}&offset={offset+limit}" + (f"&status={status}" if status else ""))

    return jsonify({"items": rep_items, "_links": links})

@app.get("/enrolments/<enrolment_id>")
def enrolment(enrolment_id: str):
    e = ENROLMENTS.get(enrolment_id)
    if not e:
        abort(404)
    return jsonify(enrolment_rep(e))

@app.patch("/enrolments/<enrolment_id>")
def enrolment_patch(enrolment_id: str):
    e = ENROLMENTS.get(enrolment_id)
    if not e:
        abort(404)

    if not can_edit(e):
        return error("FORBIDDEN", "Enrolment cannot be edited in its current state or by this role.", http_status=403)

    body = request.get_json(silent=True) or {}

    if "courseId" in body:
        cid = body["courseId"]
        if not any(c["id"] == cid for c in COURSES):
            return error("RULE_VIOLATION", "Unknown courseId.", details=[{"field": "courseId", "issue": "UNKNOWN"}])
        e.courseId = cid

    if "comment" in body:
        e.comment = str(body["comment"] or "")

    return jsonify(enrolment_rep(e))

@app.post("/enrolments/<enrolment_id>/submit")
def enrolment_submit(enrolment_id: str):
    e = ENROLMENTS.get(enrolment_id)
    if not e:
        abort(404)
    if not can_submit(e):
        return error("FORBIDDEN", "Submit not permitted.", http_status=403)

    body = request.get_json(silent=True) or {}
    if body.get("confirm") is not True:
        return error("RULE_VIOLATION", "You must confirm before submitting.",
                     details=[{"field": "confirm", "issue": "REQUIRED_TRUE"}])

    e.comment = str(body.get("comment") or e.comment or "")
    e.status = "SUBMITTED"
    return jsonify(enrolment_rep(e))

@app.post("/enrolments/<enrolment_id>/cancel")
def enrolment_cancel(enrolment_id: str):
    e = ENROLMENTS.get(enrolment_id)
    if not e:
        abort(404)
    if not can_cancel(e):
        return error("FORBIDDEN", "Cancel not permitted.", http_status=403)

    del ENROLMENTS[enrolment_id]
    return jsonify({
        "result": "cancelled",
        "_links": {"home": link("/api"), "enrolments": link("/enrolments")}
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
