import streamlit as st
import requests
from datetime import datetime

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Team Task Manager",
    page_icon="📌",
    layout="wide"
)

# =========================================
# BACKEND URL
# =========================================
BASE_URL = "http://127.0.0.1:8000"

# =========================================
# SESSION STATE
# =========================================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================================
# API FUNCTIONS
# =========================================
def signup_user(username, password, role):

    response = requests.post(
        f"{BASE_URL}/signup",
        json={
            "username": username,
            "password": password,
            "role": role
        }
    )

    return response.json()


def login_user(username, password):

    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": username,
            "password": password
        }
    )

    return response.json()


def create_project(name, description):

    response = requests.post(
        f"{BASE_URL}/projects",
        json={
            "name": name,
            "description": description
        }
    )

    return response.json()


def fetch_projects():

    response = requests.get(
        f"{BASE_URL}/projects"
    )

    return response.json()


def create_task(title, project_id, assigned_to, deadline):

    response = requests.post(
        f"{BASE_URL}/tasks",
        json={
            "title": title,
            "project_id": project_id,
            "assigned_to": assigned_to,
            "deadline": str(deadline)
        }
    )

    return response.json()


def fetch_tasks():

    response = requests.get(
        f"{BASE_URL}/tasks"
    )

    return response.json()


def update_task(task_id):

    response = requests.put(
        f"{BASE_URL}/tasks/{task_id}",
        json={
            "status": "Completed"
        }
    )

    return response.json()

# =========================================
# SIDEBAR
# =========================================
st.sidebar.title("📌 Team Task Manager")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Signup",
        "Login",
        "Dashboard"
    ]
)

# =========================================
# SIGNUP
# =========================================
if menu == "Signup":

    st.title("📝 Create Account")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    role = st.selectbox(
        "Role",
        ["Admin", "Member"]
    )

    if st.button("Create Account"):

        result = signup_user(
            username,
            password,
            role
        )

        if "message" in result:
            st.success(result["message"])
        else:
            st.error(result.get("detail", "Signup Failed"))

# =========================================
# LOGIN
# =========================================
elif menu == "Login":

    st.title("🔐 Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        result = login_user(
            username,
            password
        )

        if "token" in result:

            st.session_state.user = {
                "username": result["username"],
                "role": result["role"]
            }

            st.success("Login successful")
            st.rerun()

        else:
            st.error(result.get("detail", "Invalid Credentials"))

# =========================================
# DASHBOARD
# =========================================
elif menu == "Dashboard":

    if not st.session_state.user:
        st.warning("Please login first")
        st.stop()

    user = st.session_state.user

    st.title("📊 Dashboard")

    st.subheader(
        f"Welcome {user['username']} 👋"
    )

    st.caption(
        f"Role: {user['role']}"
    )

    # =====================================
    # ADMIN SECTION
    # =====================================
    if user["role"] == "Admin":

        st.markdown("## 📁 Create Project")

        project_name = st.text_input(
            "Project Name"
        )

        project_description = st.text_area(
            "Project Description"
        )

        if st.button("Create Project"):

            result = create_project(
                project_name,
                project_description
            )

            st.success(result["message"])

        st.divider()

        st.markdown("## ➕ Create Task")

        task_title = st.text_input(
            "Task Title"
        )

        assigned_to = st.text_input(
            "Assign To Username"
        )

        deadline = st.date_input(
            "Deadline"
        )

        projects = fetch_projects()

        project_map = {}

        for project in projects:
            project_map[
                project["name"]
            ] = project["id"]

        if project_map:

            selected_project = st.selectbox(
                "Select Project",
                list(project_map.keys())
            )

            if st.button("Add Task"):

                result = create_task(
                    task_title,
                    project_map[selected_project],
                    assigned_to,
                    deadline
                )

                st.success(result["message"])

    # =====================================
    # TASKS
    # =====================================
    st.divider()

    st.markdown("## 📋 Tasks")

    tasks = fetch_tasks()

    if not tasks:
        st.info("No tasks available")

    current_date = datetime.now()

    for task in tasks:

        overdue = False

        try:

            deadline_date = datetime.fromisoformat(
                task["deadline"]
            )

            if (
                deadline_date < current_date
                and task["status"] != "Completed"
            ):
                overdue = True

        except:
            pass

        with st.container(border=True):

            col1, col2 = st.columns([5, 1])

            with col1:

                st.subheader(task["title"])

                st.write(
                    f"📁 Project: {task['project_name']}"
                )

                st.write(
                    f"👤 Assigned To: {task['assigned_user']}"
                )

                st.write(
                    f"📌 Status: {task['status']}"
                )

                st.write(
                    f"⏰ Deadline: {task['deadline']}"
                )

                if overdue:
                    st.error("⚠️ Overdue Task")

            with col2:

                if task["status"] != "Completed":

                    if st.button(
                        "✔ Complete",
                        key=task["id"]
                    ):

                        update_task(task["id"])

                        st.rerun()

                else:
                    st.success("Done")
