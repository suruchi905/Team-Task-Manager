import streamlit as st
import requests
from datetime import datetime

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="📌 Team Task Manager",
    page_icon="📌",
    layout="wide"
)

# =========================================
# BACKEND URL
# =========================================
# Replace this with your Railway backend URL
BASE_URL = "https://your-backend-url.up.railway.app"

# =========================================
# SESSION STATE
# =========================================
if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None

# =========================================
# API HEADERS
# =========================================
def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }

# =========================================
# AUTH APIs
# =========================================
def signup_user(username, password, role):

    try:
        response = requests.post(
            f"{BASE_URL}/signup",
            json={
                "username": username,
                "password": password,
                "role": role
            }
        )

        return response.json()

    except Exception as e:
        return {
            "error": str(e)
        }


def login_user(username, password):

    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={
                "username": username,
                "password": password
            }
        )

        return response.json()

    except Exception as e:
        return {
            "error": str(e)
        }

# =========================================
# PROJECT APIs
# =========================================
def fetch_projects():

    try:
        response = requests.get(
            f"{BASE_URL}/projects",
            headers=get_headers()
        )

        return response.json()

    except:
        return []


def create_project(name, description):

    try:
        response = requests.post(
            f"{BASE_URL}/projects",
            headers=get_headers(),
            json={
                "name": name,
                "description": description
            }
        )

        return response.json()

    except Exception as e:
        return {
            "error": str(e)
        }

# =========================================
# TASK APIs
# =========================================
def fetch_tasks():

    try:
        response = requests.get(
            f"{BASE_URL}/tasks",
            headers=get_headers()
        )

        return response.json()

    except:
        return []


def create_task(title, project_id, assigned_to, deadline):

    try:
        response = requests.post(
            f"{BASE_URL}/tasks",
            headers=get_headers(),
            json={
                "title": title,
                "project_id": project_id,
                "assigned_to": assigned_to,
                "deadline": str(deadline)
            }
        )

        return response.json()

    except Exception as e:
        return {
            "error": str(e)
        }


def update_task_status(task_id, status):

    try:
        response = requests.put(
            f"{BASE_URL}/tasks/{task_id}",
            headers=get_headers(),
            json={
                "status": status
            }
        )

        return response.json()

    except Exception as e:
        return {
            "error": str(e)
        }

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
# SIGNUP PAGE
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

            elif "detail" in result:
                st.error(result["detail"])

            else:
                st.error(result.get("error", "Signup failed"))

# =========================================
# LOGIN PAGE
# =========================================
elif menu == "Login":

    st.title("🔐 Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if not username or not password:
            st.warning("Enter username and password")

        else:

            result = login_user(
                username,
                password
            )

            if "token" in result:

                st.session_state.token = result["token"]

                st.session_state.user = {
                    "username": result["username"],
                    "role": result["role"]
                }

                st.success("Login successful")
                st.rerun()

            else:
                st.error(result.get("detail", "Invalid credentials"))

# =========================================
# DASHBOARD
# =========================================
elif menu == "Dashboard":

    if not st.session_state.user:
        st.warning("Please login first")
        st.stop()

    user = st.session_state.user

    st.title("📊 Dashboard")

    col1, col2 = st.columns([4, 1])

    with col1:
        st.subheader(f"Welcome {user['username']} 👋")
        st.caption(f"Role: {user['role']}")

    with col2:
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()

    st.divider()

    # =====================================
    # ADMIN CONTROLS
    # =====================================
    if user["role"] == "Admin":

        tab1, tab2 = st.tabs([
            "📁 Create Project",
            "➕ Create Task"
        ])

        # =================================
        # CREATE PROJECT
        # =================================
        with tab1:

            st.subheader("Create New Project")

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
                        st.error(result.get("detail", "Error creating project"))

        # =================================
        # CREATE TASK
        # =================================
        with tab2:

            st.subheader("Create Task")

            task_title = st.text_input(
                "Task Title"
            )

            assigned_to = st.number_input(
                "Assign To User ID",
                min_value=1,
                step=1
            )

            deadline = st.date_input(
                "Deadline"
            )

            projects = fetch_projects()

            project_options = {}

            if isinstance(projects, list):

                for project in projects:
                    project_options[
                        project["name"]
                    ] = project["id"]

            if project_options:

                selected_project = st.selectbox(
                    "Select Project",
                    list(project_options.keys())
                )

                if st.button("Add Task"):

                    if not task_title:
                        st.warning("Task title required")

                    else:

                        result = create_task(
                            task_title,
                            project_options[selected_project],
                            assigned_to,
                            deadline
                        )

                        if "message" in result:
                            st.success(result["message"])
                            st.rerun()
                        else:
                            st.error(result.get("detail", "Task creation failed"))

            else:
                st.info("No projects available. Create project first.")

    # =====================================
    # TASK DASHBOARD
    # =====================================
    st.markdown("## 📋 Task Dashboard")

    tasks = fetch_tasks()

    total_tasks = len(tasks) if isinstance(tasks, list) else 0

    completed_tasks = 0
    pending_tasks = 0
    overdue_tasks = 0

    current_date = datetime.now()

    if isinstance(tasks, list):

        for task in tasks:

            if task["status"] == "Completed":
                completed_tasks += 1
            else:
                pending_tasks += 1

            if task.get("deadline"):

                try:
                    deadline_date = datetime.fromisoformat(
                        task["deadline"]
                    )

                    if deadline_date < current_date and task["status"] != "Completed":
                        overdue_tasks += 1

                except:
                    pass

    stat1, stat2, stat3, stat4 = st.columns(4)

    with stat1:
        st.metric("Total", total_tasks)

    with stat2:
        st.metric("Completed", completed_tasks)

    with stat3:
        st.metric("Pending", pending_tasks)

    with stat4:
        st.metric("Overdue", overdue_tasks)

    st.divider()

    # =====================================
    # TASK LIST
    # =====================================
    st.markdown("## 🗂️ All Tasks")

    if not tasks:

        st.info("No tasks found")

    else:

        for task in tasks:

            overdue = False

            if task.get("deadline"):

                try:
                    deadline_date = datetime.fromisoformat(
                        task["deadline"]
                    )

                    if deadline_date < current_date and task["status"] != "Completed":
                        overdue = True

                except:
                    pass

            with st.container(border=True):

                col1, col2 = st.columns([5, 1])

                with col1:

                    st.subheader(task["title"])

                    st.write(
                        f"📁 Project: {task.get('project_name', 'N/A')}"
                    )

                    st.write(
                        f"👤 Assigned To: {task.get('assigned_user', 'N/A')}"
                    )

                    st.write(
                        f"📌 Status: {task['status']}"
                    )

                    if task.get("deadline"):
                        st.write(
                            f"⏰ Deadline: {task['deadline']}"
                        )

                    if overdue:
                        st.error("⚠️ Overdue Task")

                with col2:

                    if task["status"] != "Completed":

                        if st.button(
                            "✔ Complete",
                            key=f"complete_{task['id']}"
                        ):

                            result = update_task_status(
                                task["id"],
                                "Completed"
                            )

                            if "message" in result:
                                st.success("Task updated")
                                st.rerun()
                            else:
                                st.error("Failed to update")

                    else:
                        st.success("Done")

# =========================================
# FOOTER
# =========================================
st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit + FastAPI")
