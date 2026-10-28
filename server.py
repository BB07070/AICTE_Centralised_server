import sqlite3, uuid, os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB = "complaints.db"

USERS = {
    "pgrc_admin": {"pw": "admin123", "dept": "PGRC"},
    "rb_admin": {"pw": "admin123", "dept": "RB"},
    "reg_admin": {"pw": "admin123", "dept": "REGIONAL"},
    "super_master": {"pw": "master123", "dept": "MASTER"}
}

SESSIONS = {}
RULES = {"fees": "PGRC", "harassment": "PGRC", "affiliation": "RB", "faculty": "RB", "infrastructure": "REGIONAL"}
DEFAULT_DEPT = "PGRC"

app = FastAPI(title="Mini AICTE - Authenticated Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init():
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS complaints(
        id TEXT PRIMARY KEY, institution TEXT, category TEXT,
        description TEXT, department TEXT, status TEXT, created_at TEXT, ip_address TEXT);
    CREATE TABLE IF NOT EXISTS actions(
        id INTEGER PRIMARY KEY AUTOINCREMENT, complaint_id TEXT,
        department TEXT, action TEXT, at TEXT, ip_address TEXT);
    """)
    con.commit()
    con.close()

init()

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def who_is(token):
    dept = SESSIONS.get(token)
    if not dept: raise HTTPException(401, "Unauthorized: Please login first.")
    return dept

def get_ip(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded: return forwarded.split(",")[0]
    return request.client.host

class NewComplaint(BaseModel): institution: str; category: str; description: str
class NewAction(BaseModel): action: str; status: Optional[str] = None; force: bool = False
class LoginReq(BaseModel): username: str; password: str

@app.post("/login")
def login(creds: LoginReq):
    user = USERS.get(creds.username)
    if not user or user["pw"] != creds.password:
        raise HTTPException(401, "Invalid username or password")
    session_token = uuid.uuid4().hex
    SESSIONS[session_token] = user["dept"]
    return {"token": session_token, "department": user["dept"], "message": f"Welcome, {creds.username}"}

@app.post("/complaints")
def create_complaint(c: NewComplaint, request: Request):
    ip = get_ip(request)
    dept = RULES.get(c.category.lower().strip(), DEFAULT_DEPT)
    cid = "C-" + uuid.uuid4().hex[:6].upper()
    con = db()
    con.execute("INSERT INTO complaints VALUES (?,?,?,?,?,?,?,?)",
                (cid, c.institution.strip(), c.category, c.description, dept, "Pending", now(), ip))
    con.execute("INSERT INTO actions(complaint_id, department, action, at, ip_address) VALUES (?,?,?,?,?)",
                (cid, "SYSTEM", f"Registered and routed to {dept}", now(), "127.0.0.1"))
    con.commit()
    con.close()
    return {"complaint_id": cid, "assigned_to": dept, "origin_ip": ip}

@app.get("/track/{cid}")
def track(cid: str):
    con = db()
    c = con.execute("SELECT * FROM complaints WHERE id=?", (cid,)).fetchone()
    if not c: raise HTTPException(404, "Complaint not found")
    last = con.execute("SELECT action, at FROM actions WHERE complaint_id=? ORDER BY id DESC LIMIT 1", (cid,)).fetchone()
    con.close()
    return {"complaint_id": cid, "status": c["status"], "department": c["department"], "last_action": last["action"] if last else "None"}

@app.get("/complaints")
def list_all(x_token: str = Header(None)):
    who_is(x_token)
    con = db()
    rows = con.execute("SELECT id, institution, category, department, status, ip_address FROM complaints ORDER BY created_at").fetchall()
    con.close()
    return [dict(r) for r in rows]

@app.get("/complaints/{cid}")
def view(cid: str, x_token: str = Header(None)):
    who_is(x_token)
    con = db()
    c = con.execute("SELECT * FROM complaints WHERE id=?", (cid,)).fetchone()
    if not c: raise HTTPException(404, "Complaint not found")
    acts = con.execute("SELECT department, action, at, ip_address FROM actions WHERE complaint_id=? ORDER BY id", (cid,)).fetchall()
    con.close()
    return {"complaint": dict(c), "history": [dict(a) for a in acts]}

@app.post("/complaints/{cid}/actions")
def add_action(cid: str, a: NewAction, request: Request, x_token: str = Header(None)):
    who = who_is(x_token)
    ip = get_ip(request)
    con = db()
    c = con.execute("SELECT * FROM complaints WHERE id=?", (cid,)).fetchone()
    if not c: raise HTTPException(404, "Complaint not found")
    if who != "MASTER" and who != c["department"]:
        raise HTTPException(403, f"Access Denied: You are {who}. Only {c['department']} or MASTER can act on this.")
    con.execute("INSERT INTO actions(complaint_id, department, action, at, ip_address) VALUES (?,?,?,?,?)",
                (cid, who, a.action, now(), ip))
    new_status = a.status or ("Under Process" if c["status"] == "Pending" else c["status"])
    con.execute("UPDATE complaints SET status=? WHERE id=?", (new_status, cid))
    con.commit()
    con.close()
    return {"ok": True, "logged_by": who, "status": new_status, "ip": ip}

@app.delete("/complaints/{cid}")
def delete_complaint(cid: str, x_token: str = Header(None)):
    who = who_is(x_token)
    if who != "MASTER": raise HTTPException(403, "Master privileges required.")
    con = db()
    con.execute("DELETE FROM complaints WHERE id=?", (cid,))
    con.execute("DELETE FROM actions WHERE complaint_id=?", (cid,))
    con.commit()
    con.close()
    return {"ok": True, "message": "Deleted"}

@app.post("/shutdown")
def shutdown_server(x_token: str = Header(None)):
    who = who_is(x_token)
    if who != "MASTER": raise HTTPException(403, "Master privileges required.")
    os._exit(0)