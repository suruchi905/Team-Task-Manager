import streamlit as st
import sqlite3

# =========================
# DB SETUP
# =========================
conn = sqlite3.connect("task_manager.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    assigned_to TEXT,
    status TEXT
)
""")

conn.commit()

# =========================
# SESSION STATE
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# APP UI
# =========================
st.set_page_config(page_title="Team Task Manager", layout="centered")
st.title("📌 Team Task Manager (Full Stack - Streamlit)")

menu = st.sidebar.radio("Menu", ["Signup", "Login", "Dashboard"])

# =========================
# SIGNUP
# =========================
if menu == "Signup":
    st.subheader("Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Admin", "Member"])

    if st.button("Signup"):
        try:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role)
            )
            conn.commit()
            st.success("Account created successfully!")
        except:
            st.error("Username already exists!")

# =========================
# LOGIN
# =========================
elif menu == "Login":
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            st.session_state.user = {
                "id": user[0],
                "username": user[1],
                "role": user[3]
            }
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

# =========================
# DASHBOARD
# =========================
elif menu == "Dashboard":

    if st.session_state.user is None:
        st.warning("Please login first")
        st.stop()

    st.subheader(f"Welcome {st.session_state.user['username']} ({st.session_state.user['role']})")

    # =========================
    # CREATE TASK
    # =========================
    st.markdown("### ➕ Create Task")

    title = st.text_input("Task Title")
    assigned = st.text_input("Assign To")

    if st.button("Add Task"):
        if title and assigned:
            cursor.execute(
                "INSERT INTO tasks (title, assigned_to, status) VALUES (?, ?, ?)",
                (title, assigned, "Pending")
            )
            conn.commit()
            st.success("Task created!")
        else:
            st.warning("Fill all fields")

    # =========================
    # TASK LIST
    # =========================
    st.markdown("### 📋 All Tasks")

    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    for t in tasks:
        col1, col2, col3 = st.columns([4,2,2])

        with col1:
            st.write(f"**{t[1]}** → {t[2]}")

        with col2:
            st.write(t[3])

        with col3:
            if st.button("✔ Done", key=t[0]):
                cursor.execute(
                    "UPDATE tasks SET status='Completed' WHERE id=?",
                    (t[0],)
                )
                conn.commit()
                st.rerun()
