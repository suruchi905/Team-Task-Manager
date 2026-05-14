import streamlit as st
import requests
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="📌 Team Task Manager",
    page_icon="📌",
    layout="wide"
)

# =========================================================
# BACKEND URL
# =========================================================
# IMPORTANT:
# Replace with your REAL Railway backend URL

BASE_URL = "https://your-railway-backend.up.railway.app"

# Example:
# BASE_URL = "https://team-task-manager-production.up.railway.app"

# =========================================================
# SESSION STATE
# =========================================================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================================================
# SAFE REQUEST FUNCTION
# =========================================================
def safe_request(method, endpoint, data=None):

    url = f"{BASE_URL}{endpoint}"

    try:

        if method == "GET":

            response = requests.get(
                url,
                timeout=10
            )

        elif method == "POST":

            response = requests.post(
                url,
                json=data,
                timeout=10
            )

        elif method == "PUT":

            response = requests.put(
                url,
                json=data,
                timeout=10
            )

        else:

            return {
                "detail": "Invalid request method"
            }

        # =====================================
        # HANDLE BAD STATUS
        # =====================================
        if response.status_code >= 400:

            try:
                return response.json()

            except:
                return {
                    "detail": response.text
                }

        return response.json()

    except requests.exceptions.ConnectionError:

        return {
            "detail": "❌ Backend connection failed. Check Railway deployment."
        }

    except requests.exceptions.Timeout:

        return {
            "detail": "❌ Request timeout. Backend may be sleeping."
        }

    except Exception as e:

        return {
            "detail": str(e)
        }

# =========================================================
# API FUNCTIONS
# =========================================================
def signup_user(username, password, role):

    return safe_request(
        "POST",
        "/signup",
        {
            "username": username,
            "password": password,
            "role": role
        }
    )


def login_user(username, password):

    return safe_request(
        "POST",
        "/login",
        {
            "username": username,
            "password": password
        }
    )


def create_project(name, description):

    return safe_request(
        "POST",
        "/projects",
        {
            "name": name,
            "description": description
        }
    )


def fetch_projects():

    result = safe_request(
        "GET",
        "/projects"
    )

    if isinstance(result, list):
        return result

    return []


def create_task(title, project_id, assigned_to, deadline):

    return safe_request(
        "POST",
        "/tasks",
        {
            "title": title,
            "project_id": project_id,
            "assigned_to": assigned_to,
            "deadline": str(deadline)
        }
    )


def fetch_tasks():

    result = safe_request(
        "GET",
        "/tasks"
    )

    if isinstance(result, list):
        return result

    return []


def update_task(task_id):

    return safe_request(
        "PUT",
        f"/tasks/{task_id}",
        {
            "status": "Completed"
        }
    )

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("📌 Team Task Manager")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Signup",
        "Login",
        "Dashboard"
    ]
)

# =========================================================
# SIGNUP PAGE
# =========================================================
if menu == "Signup":

    st.title("📝 Create Account")

    username = st.text_input(
        "Username"
    )

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

            st.warning(
                "Please fill all fields"
            )

        elif len(password) < 6:

            st.warning(
                "Password must be at least 6 characters"
            )

        else:

            result = signup_user(
                username,
                password,
                role
            )

            if "message" in result:

                st.success(
                    result["message"]
                )

            else:

                st.error(
                    result.get(
                        "detail",
                        "Signup failed"
                    )
                )

# =========================================================
# LOGIN PAGE
# =========================================================
elif menu == "Login":

    st.title("🔐 Login")

    username = st.text_input(
        "Username"
    )

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

            st.success(
                "✅ Login successful"
            )

            st.rerun()

        else:

            st.error(
                result.get(
                    "detail",
                    "Invalid credentials"
                )
            )

# =========================================================
# DASHBOARD PAGE
# =========================================================
elif menu == "Dashboard":

    if not st.session_state.user:

        st.warning(
            "Please login first"
        )

        st.stop()

    user = st.session_state.user

    st.title("📊 Dashboard")

    st.subheader(
        f"Welcome {user['username']} 👋"
    )

    st.caption(
        f"Role: {user['role']}"
    )

    # =====================================================
    # LOGOUT
    # =====================================================
    if st.button("Logout"):

        st.session_state.user = None

        st.rerun()

    st.divider()

    # =====================================================
    # ADMIN SECTION
    # =====================================================
    if user["role"] == "Admin":

        st.markdown(
            "## 📁 Create Project"
        )

        project_name = st.text_input(
            "Project Name"
        )

        project_description = st.text_area(
            "Project Description"
        )

        if st.button("Create Project"):

            if not project_name:

                st.warning(
                    "Project name required"
                )

            else:

                result = create_project(
                    project_name,
                    project_description
                )

                if "message" in result:

                    st.success(
                        result["message"]
                    )

                else:

                    st.error(
                        result.get(
                            "detail",
                            "Project creation failed"
                        )
                    )

        st.divider()

        st.markdown(
            "## ➕ Create Task"
        )

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

                if not task_title or not assigned_to:

                    st.warning(
                        "Please fill all task fields"
                    )

                else:

                    result = create_task(
                        task_title,
                        project_map[selected_project],
                        assigned_to,
                        deadline
                    )

                    if "message" in result:

                        st.success(
                            result["message"]
                        )

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
                "No projects found. Create project first."
            )

    # =====================================================
    # TASK LIST
    # =====================================================
    st.markdown(
        "## 📋 All Tasks"
    )

    tasks = fetch_tasks()

    if not tasks:

        st.info(
            "No tasks available"
        )

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

                    st.subheader(
                        task["title"]
                    )

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

                        st.error(
                            "⚠️ Overdue Task"
                        )

                with col2:

                    if task["status"] != "Completed":

                        if st.button(
                            "✔ Complete",
                            key=task["id"]
                        ):

                            update_task(
                                task["id"]
                            )

                            st.rerun()

                    else:

                        st.success(
                            "Done"
                        )
