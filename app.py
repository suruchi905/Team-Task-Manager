import streamlit as st
import sqlite3
from datetime import datetime, date
import hashlib

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="📌 Team Task Manager",
    page_icon="📌",
    layout="wide"
)

# =====================================================
# DATABASE
# =====================================================
conn = sqlite3.connect(
    "team_task_manager.db",
    check_same_thread=False
)

cursor = conn.cursor()

# =====================================================
# CREATE TABLES
# =====================================================
cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    '''
)

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        created_by TEXT
    )
    '''
)

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        project_name TEXT,
        assigned_to TEXT,
        deadline TEXT,
        status TEXT
    )
    '''
)

conn.commit()

# =====================================================
# SESSION STATE
# =====================================================
if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================
# PASSWORD HASHING
# =====================================================
def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()

# =====================================================
# USER FUNCTIONS
# =====================================================
def signup_user(username, password, role):

    try:

        hashed_password = hash_password(
            password
        )

        cursor.execute(
            """
            INSERT INTO users
            (username, password, role)
            VALUES (?, ?, ?)
            """,
            (
                username,
                hashed_password,
                role
            )
        )

        conn.commit()

        return True, "✅ Account created successfully"

    except sqlite3.IntegrityError:

        return False, "❌ Username already exists"

# =====================================================
# LOGIN
# =====================================================
def login_user(username, password):

    hashed_password = hash_password(
        password
    )

    cursor.execute(
        """
        SELECT * FROM users
        WHERE username=? AND password=?
        """,
        (
            username,
            hashed_password
        )
    )

    return cursor.fetchone()

# =====================================================
# PROJECT FUNCTIONS
# =====================================================
def create_project(name, description, created_by):

    cursor.execute(
        """
        INSERT INTO projects
        (name, description, created_by)
        VALUES (?, ?, ?)
        """,
        (
            name,
            description,
            created_by
        )
    )

    conn.commit()

# =====================================================
# GET PROJECTS
# =====================================================
def get_projects():

    cursor.execute(
        "SELECT * FROM projects"
    )

    return cursor.fetchall()

# =====================================================
# CREATE TASK
# =====================================================
def create_task(
    title,
    project_name,
    assigned_to,
    deadline
):

    cursor.execute(
        """
        INSERT INTO tasks
        (title, project_name,
        assigned_to, deadline, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            title,
            project_name,
            assigned_to,
            str(deadline),
            "Pending"
        )
    )

    conn.commit()

# =====================================================
# GET TASKS
# =====================================================
def get_tasks():

    cursor.execute(
        "SELECT * FROM tasks"
    )

    return cursor.fetchall()

# =====================================================
# COMPLETE TASK
# =====================================================
def complete_task(task_id):

    cursor.execute(
        """
        UPDATE tasks
        SET status=?
        WHERE id=?
        """,
        (
            "Completed",
            task_id
        )
    )

    conn.commit()

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title(
    "📌 Team Task Manager"
)

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

            success, message = signup_user(
                username,
                password,
                role
            )

            if success:

                st.success(message)

            else:

                st.error(message)

# =====================================================
# LOGIN PAGE
# =====================================================
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

        user = login_user(
            username,
            password
        )

        if user:

            st.session_state.user = {
                "id": user[0],
                "username": user[1],
                "role": user[3]
            }

            st.success(
                "✅ Login successful"
            )

            st.rerun()

        else:

            st.error(
                "❌ Invalid username or password"
            )

# =====================================================
# DASHBOARD PAGE
# =====================================================
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

                create_project(
                    project_name,
                    project_description,
                    user["username"]
                )

                st.success(
                    "✅ Project created successfully"
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
            "Deadline",
            min_value=date.today()
        )

        projects = get_projects()

        project_names = [
            project[1]
            for project in projects
        ]

        if project_names:

            selected_project = st.selectbox(
                "Select Project",
                project_names
            )

            if st.button("Add Task"):

                if not task_title or not assigned_to:

                    st.warning(
                        "Please fill all fields"
                    )

                else:

                    create_task(
                        task_title,
                        selected_project,
                        assigned_to,
                        deadline
                    )

                    st.success(
                        "✅ Task created successfully"
                    )

                    st.rerun()

        else:

            st.info(
                "Create a project first"
            )

    # =================================================
    # TASK LIST
    # =================================================
    st.markdown(
        "## 📋 All Tasks"
    )

    tasks = get_tasks()

    if not tasks:

        st.info(
            "No tasks available"
        )

    else:

        current_date = datetime.now().date()

        for task in tasks:

            task_id = task[0]
            title = task[1]
            project_name = task[2]
            assigned_to = task[3]
            deadline = task[4]
            status = task[5]

            overdue = False

            try:

                deadline_date = datetime.strptime(
                    deadline,
                    "%Y-%m-%d"
                ).date()

                if (
                    deadline_date < current_date
                    and status != "Completed"
                ):

                    overdue = True

            except:
                pass

            with st.container(border=True):

                col1, col2 = st.columns([5, 1])

                with col1:

                    st.subheader(title)

                    st.write(
                        f"📁 Project: {project_name}"
                    )

                    st.write(
                        f"👤 Assigned To: {assigned_to}"
                    )

                    st.write(
                        f"📌 Status: {status}"
                    )

                    st.write(
                        f"⏰ Deadline: {deadline}"
                    )

                    if overdue:

                        st.error(
                            "⚠️ Overdue Task"
                        )

                with col2:

                    if status != "Completed":

                        if st.button(
                            "✔ Complete",
                            key=f"complete_{task_id}"
                        ):

                            complete_task(task_id)

                            st.rerun()

                    else:

                        st.success("Done")
