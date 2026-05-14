import streamlit as st
import requests
from datetime import datetime

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="📌 Team Task Manager",
    page_icon="📌",
    layout="wide"
)

# =====================================================
# BACKEND URL
# =====================================================
# Replace with your Railway backend URL after deployment

BASE_URL = "https://your-backend-url.up.railway.app"

# =====================================================
# SESSION STATE
# =====================================================
if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================
# API FUNCTIONS
# =====================================================
def signup_user(username, password, role):

    try:

        response = requests.post(
            f"{BASE_URL}/signup",
            json={
                "username": username,
                "password": password,
                "role": role
            },
            timeout=10
        )

        return response.json()

    except requests.exceptions.ConnectionError:

        return {
            "detail": "❌ Cannot connect to backend server"
        }

    except Exception as e:

        return {
            "detail": str(e)
        }


def login_user(username, password):

    try:

        response = requests.post(
            f"{BASE_URL}/login",
            json={
                "username": username,
                "password": password
            },
            timeout=10
        )

        return response.json()

    except requests.exceptions.ConnectionError:

        return {
            "detail": "❌ Cannot connect to backend server"
        }

    except Exception as e:

        return {
            "detail": str(e)
        }


def create_project(name, description):

    try:

        response = requests.post(
            f"{BASE_URL}/projects",
            json={
                "name": name,
                "description": description
            },
            timeout=10
        )

        return response.json()

    except Exception as e:

        return {
            "detail": str(e)
        }


def fetch_projects():

    try:

        response = requests.get(
            f"{BASE_URL}/projects",
            timeout=10
        )

        return response.json()

    except:
        return []


def create_task(title, project_id, assigned_to, deadline):

    try:

        response = requests.post(
            f"{BASE_URL}/tasks",
            json={
                "title": title,
                "project_id": project_id,
                "assigned_to": assigned_to,
                "deadline": str(deadline)
            },
            timeout=10
        )

        return response.json()

    except Exception as e:

        return {
            "detail": str(e)
        }


def fetch_tasks():

    try:

        response = requests.get(
            f"{BASE_URL}/tasks",
            timeout=10
        )

        return response.json()

    except:
        return []


def update_task(task_id):

    try:

        response = requests.put(
            f"{BASE_URL}/tasks/{task_id}",
            json={
                "status": "Completed"
            },
            timeout=10
        )

        return response.json()

    except Exception as e:

        return {
            "detail": str(e)
        }

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("📌 Team Task Manager")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Signup",
        "Login",
        "Dashboard"
    ]
)

# =====================================================
# SIGNUP PAGE
# =====================================================
if menu == "Signup":

    st.title("📝 Create Account")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    role = st.selectbox(
        "Role",
        [
            "Admin",
            "Member"
        ]
    )

    if st.button("Create Account"):

        if not username or not password:

            st.warning("Please fill all fields")

        elif len(password) < 6:

            st.warning("Password must be at least 6 characters")

        else:

            result = signup_user(
                username,
                password,
                role
            )

            if "message" in result:

                st.success(result["message"])

            else:

                st.error(
                    result.get(
                        "detail",
                        "Signup failed"
                    )
                )

# =====================================================
# LOGIN PAGE
# =====================================================
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

            st.success("✅ Login successful")

            st.rerun()

        else:

            st.error(
                result.get(
                    "detail",
                    "Invalid credentials"
                )
            )

# =====================================================
# DASHBOARD PAGE
# =====================================================
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

    # =================================================
    # LOGOUT
    # =================================================
    if st.button("Logout"):

        st.session_state.user = None

        st.rerun()

    st.divider()

    # =================================================
    # ADMIN SECTION
    # =================================================
    if user["role"] == "Admin":

        st.markdown("## 📁 Create Project")

        project_name = st.text_input(
            "Project Name"
        )

        project_description = st.text_area(
            "Project Description"
        )

        if st.button("Create Project"):

            if not project_name:

                st.warning("Project name required")

            else:

                result = create_project(
                    project_name,
                    project_description
                )

                if "message" in result:

                    st.success(result["message"])

                else:

                    st.error(
                        result.get(
                            "detail",
                            "Project creation failed"
                        )
                    )

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

        if isinstance(projects, list):

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

                if not task_title or not assigned_to:

                    st.warning("Fill all task fields")

                else:

                    result = create_task(
                        task_title,
                        project_map[selected_project],
                        assigned_to,
                        deadline
                    )

                    if "message" in result:

                        st.success(result["message"])

                        st.rerun()

                    else:

                        st.error(
                            result.get(
                                "detail",
                                "Task creation failed"
                            )
                        )

        else:

            st.info(
                "No projects available. Create project first."
            )

    # =================================================
    # TASK LIST
    # =================================================
    st.markdown("## 📋 All Tasks")

    tasks = fetch_tasks()

    if not tasks:

        st.info("No tasks available")

    else:

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
