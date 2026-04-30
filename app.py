import streamlit as st
import requests
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import threading
import uvicorn

# ================= BACKEND =================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    status TEXT,
    assigned_to INTEGER
)
""")

conn.commit()

# AUTH
@app.post("/signup")
def signup(email: str, password: str, role: str):
    cursor.execute("INSERT INTO users VALUES (NULL,?,?,?)",
                   (email, password, role))
    conn.commit()
    return {"msg": "User created"}

@app.post("/login")
def login(email: str, password: str):
    user = cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    ).fetchone()

    if not user:
        raise HTTPException(400, "Invalid credentials")

    return {"user_id": user[0], "role": user[3]}

# TASKS
@app.post("/tasks")
def create_task(title: str, assigned_to: int):
    cursor.execute("INSERT INTO tasks VALUES (NULL,?,?,?)",
                   (title, "Todo", assigned_to))
    conn.commit()
    return {"msg": "Task created"}

@app.get("/tasks/{user_id}")
def get_tasks(user_id: int):
    tasks = cursor.execute(
        "SELECT * FROM tasks WHERE assigned_to=?",
        (user_id,)
    ).fetchall()

    return [{"id": t[0], "title": t[1], "status": t[2]} for t in tasks]

@app.put("/tasks/{task_id}")
def update_task(task_id: int, status: str):
    cursor.execute("UPDATE tasks SET status=? WHERE id=?",
                   (status, task_id))
    conn.commit()
    return {"msg": "Updated"}

# Run backend in background
def run_api():
    uvicorn.run(app, host="127.0.0.1", port=8000)

threading.Thread(target=run_api, daemon=True).start()

# ================= FRONTEND =================

API = "http://127.0.0.1:8000"

st.title("Team Task Manager")

menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

# SIGNUP
if menu == "Signup":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["admin", "member"])

    if st.button("Signup"):
        requests.post(f"{API}/signup", params={
            "email": email,
            "password": password,
            "role": role
        })
        st.success("User created")

# LOGIN
if menu == "Login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(f"{API}/login", params={
            "email": email,
            "password": password
        })

        if res.status_code == 200:
            data = res.json()
            st.session_state["user_id"] = data["user_id"]
            st.session_state["role"] = data["role"]
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

# DASHBOARD
if "user_id" in st.session_state:
    st.subheader("Dashboard")

    user_id = st.session_state["user_id"]
    role = st.session_state["role"]

    st.write("Role:", role)

    if role == "admin":
        title = st.text_input("Task Title")
        assigned = st.number_input("Assign User ID", step=1)

        if st.button("Create Task"):
            requests.post(f"{API}/tasks", params={
                "title": title,
                "assigned_to": assigned
            })
            st.success("Task created")

    st.markdown("### Tasks")

    res = requests.get(f"{API}/tasks/{user_id}")
    tasks = res.json()

    for t in tasks:
        st.write(f"{t['title']} - {t['status']}")

        new_status = st.selectbox(
            f"Update {t['id']}",
            ["Todo", "In Progress", "Done"],
            key=str(t["id"])
        )

        if st.button(f"Update {t['id']}"):
            requests.put(
                f"{API}/tasks/{t['id']}",
                params={"status": new_status}
            )
            st.success("Updated")
