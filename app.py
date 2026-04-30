import streamlit as st
import json
import os

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="Team Task Manager", page_icon="📋", layout="centered")

DATA_FILE = "tasks.json"

# ---------------------------
# LOAD TASKS
# ---------------------------
def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# ---------------------------
# SAVE TASKS
# ---------------------------
def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

# ---------------------------
# INIT
# ---------------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

# ---------------------------
# UI HEADER
# ---------------------------
st.title("📋 Team Task Manager")
st.write("Simple Streamlit full-stack app (Frontend + Backend merged)")

# ---------------------------
# ADD TASK
# ---------------------------
st.subheader("➕ Add New Task")

task_title = st.text_input("Task Title")
task_desc = st.text_area("Task Description")

if st.button("Add Task"):
    if task_title.strip() == "":
        st.error("Task title cannot be empty")
    else:
        new_task = {
            "title": task_title,
            "description": task_desc,
            "done": False
        }
        st.session_state.tasks.append(new_task)
        save_tasks(st.session_state.tasks)
        st.success("Task added successfully!")
        st.rerun()

# ---------------------------
# SHOW TASKS
# ---------------------------
st.subheader("📌 Your Tasks")

if len(st.session_state.tasks) == 0:
    st.info("No tasks yet. Add one above 👆")

for i, task in enumerate(st.session_state.tasks):
    col1, col2, col3 = st.columns([5, 1, 1])

    with col1:
        status = "✅" if task["done"] else "⏳"
        st.markdown(f"**{status} {task['title']}**")
        st.caption(task["description"])

    with col2:
        if st.button("✔️", key=f"done_{i}"):
            st.session_state.tasks[i]["done"] = True
            save_tasks(st.session_state.tasks)
            st.rerun()

    with col3:
        if st.button("🗑️", key=f"del_{i}"):
            st.session_state.tasks.pop(i)
            save_tasks(st.session_state.tasks)
            st.rerun()

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.caption("Built with Streamlit 🚀")
