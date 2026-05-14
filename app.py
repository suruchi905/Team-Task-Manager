import streamlit as st
import requests

# ======================================
# APP CONFIG
# ======================================
st.set_page_config(
    page_title="Team Task Manager",
    page_icon="📌",
    layout="centered"
)

# ======================================
# API CONFIG
# ======================================
BASE_URL = "http://127.0.0.1:8000"

# ======================================
# SESSION STATE
# ======================================
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ======================================
# HELPER FUNCTIONS
# ======================================
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


def fetch_tasks():
    response = requests.get(
        f"{BASE_URL}/tasks"
    )

    return response.json()["tasks"]


def add_task(title, assigned_to):
    response = requests.post(
        f"{BASE_URL}/tasks",
        json={
            "title": title,
            "assigned_to": assigned_to
        }
    )

    return response.json()


def complete_task(task_id):
    response = requests.put(
        f"{BASE_URL}/tasks/{task_id}"
    )

    return response.json()


# ======================================
# PAGE HEADER
# ======================================
st.title("📌 Team Task Manager")

# ======================================
# SIDEBAR
# ======================================
menu = st.sidebar.radio(
    "Navigation",
    ["Signup", "Login", "Dashboard"]
)

# ======================================
# SIGNUP PAGE
# ======================================
if menu == "Signup":

    st.subheader("Create Account")

    username = st.text_input(
        "Username"
    )

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
            st.warning("Please fill all fields.")

        else:
            result = signup_user(
                username,
                password,
                role
            )

            if "message" in result:
                st.success(result["message"])

            else:
                st.error(result["error"])


# ======================================
# LOGIN PAGE
# ======================================
elif menu == "Login":

    st.subheader("Login")

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if not username or not password:
            st.warning("Enter username and password.")

        else:
            result = login_user(
                username,
                password
            )

            if result["success"]:

                st.session_state.current_user = {
                    "username": result["username"],
                    "role": result["role"]
                }

                st.success("Login successful!")

            else:
                st.error("Invalid credentials")


# ======================================
# DASHBOARD
# ======================================
elif menu == "Dashboard":

    if not st.session_state.current_user:
        st.warning("Please login first.")
        st.stop()

    user = st.session_state.current_user

    st.subheader(
        f"Welcome {user['username']} 👋"
    )

    st.caption(
        f"Role: {user['role']}"
    )

    # ==================================
    # CREATE TASK
    # ==================================
    st.markdown("## ➕ Create Task")

    task_title = st.text_input(
        "Task Title"
    )

    assigned_user = st.text_input(
        "Assign To"
    )

    if st.button("Add Task"):

        if not task_title or not assigned_user:
            st.warning("Please fill all fields.")

        else:
            add_task(
                task_title,
                assigned_user
            )

            st.success("Task created successfully!")

    # ==================================
    # TASK LIST
    # ==================================
    st.markdown("## 📋 All Tasks")

    tasks = fetch_tasks()

    if not tasks:
        st.info("No tasks available.")

    for task in tasks:

        task_id = task[0]
        task_title = task[1]
        assigned_to = task[2]
        status = task[3]

        col1, col2, col3 = st.columns([4, 2, 2])

        with col1:
            st.write(
                f"**{task_title}** → {assigned_to}"
            )

        with col2:
            st.write(status)

        with col3:

            if status != "Completed":

                if st.button(
                    "✔ Complete",
                    key=f"complete_{task_id}"
                ):

                    complete_task(task_id)

                    st.rerun()

            else:
                st.write("Done ✅")
