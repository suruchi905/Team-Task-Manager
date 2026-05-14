# Full Team Task Manager (FastAPI + Streamlit + MongoDB)

## 📁 Project Structure

```bash
team-task-manager/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app.py
│   └── requirements.txt
│
└── README.md
```

---

# ==============================

# BACKEND CODE

# File: backend/main.py

# ==============================

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import os

# ==========================================
# APP
# ==========================================
app = FastAPI()

# ==========================================
# CORS
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# MONGODB
# ==========================================
MONGO_URL = "mongodb://localhost:27017"

client = MongoClient(MONGO_URL)

db = client["team_task_manager"]

users_collection = db["users"]
projects_collection = db["projects"]
tasks_collection = db["tasks"]

# ==========================================
# SECURITY
# ==========================================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY = "SECRET123"
ALGORITHM = "HS256"

# ==========================================
# SCHEMAS
# ==========================================
class SignupModel(BaseModel):
    username: str
    password: str
    role: str


class LoginModel(BaseModel):
    username: str
    password: str


class ProjectModel(BaseModel):
    name: str
    description: Optional[str] = ""


class TaskModel(BaseModel):
    title: str
    project_id: str
    assigned_to: str
    deadline: str


class UpdateTaskModel(BaseModel):
    status: str

# ==========================================
# HELPERS
# ==========================================
def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_token(data: dict):

    payload = data.copy()

    payload["exp"] = datetime.utcnow() + timedelta(days=1)

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

# ==========================================
# HOME
# ==========================================
@app.get("/")
def home():
    return {
        "message": "Team Task Manager API Running"
    }

# ==========================================
# SIGNUP
# ==========================================
@app.post("/signup")
def signup(data: SignupModel):

    existing_user = users_collection.find_one({
        "username": data.username
    })

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    user = {
        "username": data.username,
        "password": hash_password(data.password),
        "role": data.role
    }

    users_collection.insert_one(user)

    return {
        "message": "Account created successfully"
    }

# ==========================================
# LOGIN
# ==========================================
@app.post("/login")
def login(data: LoginModel):

    user = users_collection.find_one({
        "username": data.username
    })

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        data.password,
        user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_token({
        "username": user["username"],
        "role": user["role"]
    })

    return {
        "token": token,
        "username": user["username"],
        "role": user["role"]
    }

# ==========================================
# CREATE PROJECT
# ==========================================
@app.post("/projects")
def create_project(data: ProjectModel):

    project = {
        "name": data.name,
        "description": data.description
    }

    result = projects_collection.insert_one(project)

    return {
        "message": "Project created successfully",
        "project_id": str(result.inserted_id)
    }

# ==========================================
# GET PROJECTS
# ==========================================
@app.get("/projects")
def get_projects():

    projects = []

    for project in projects_collection.find():

        projects.append({
            "id": str(project["_id"]),
            "name": project["name"],
            "description": project.get("description", "")
        })

    return projects

# ==========================================
# CREATE TASK
# ==========================================
@app.post("/tasks")
def create_task(data: TaskModel):

    task = {
        "title": data.title,
        "project_id": data.project_id,
        "assigned_to": data.assigned_to,
        "deadline": data.deadline,
        "status": "Pending"
    }

    result = tasks_collection.insert_one(task)

    return {
        "message": "Task created successfully",
        "task_id": str(result.inserted_id)
    }

# ==========================================
# GET TASKS
# ==========================================
@app.get("/tasks")
def get_tasks():

    tasks = []

    for task in tasks_collection.find():

        project = projects_collection.find_one({
            "_id": ObjectId(task["project_id"])
        })

        tasks.append({
            "id": str(task["_id"]),
            "title": task["title"],
            "project_name": project["name"] if project else "N/A",
            "assigned_user": task["assigned_to"],
            "deadline": task["deadline"],
            "status": task["status"]
        })

    return tasks

# ==========================================
# UPDATE TASK
# ==========================================
@app.put("/tasks/{task_id}")
def update_task(task_id: str, data: UpdateTaskModel):

    tasks_collection.update_one(
        {
            "_id": ObjectId(task_id)
        },
        {
            "$set": {
                "status": data.status
            }
        }
    )

    return {
        "message": "Task updated successfully"
    }
```

---

# ========================================

# FRONTEND CODE

# File: frontend/app.py

# ========================================

```python
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
BASE_URL = "http://127.0.0.1:8000"

# =========================================
# SESSION STATE
# =========================================
if "token" not in st.session_state:
    st.session_state.token = None

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


def fetch_projects():

    response = requests.get(
        f"{BASE_URL}/projects"
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


def fetch_tasks():

    response = requests.get(
        f"{BASE_URL}/tasks"
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


def update_task(task_id, status):

    response = requests.put(
        f"{BASE_URL}/tasks/{task_id}",
        json={
            "status": status
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
            st.error(result.get("detail", "Signup failed"))

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

    st.subheader(f"Welcome {user['username']} 👋")
    st.caption(f"Role: {user['role']}")

    # =====================================
    # ADMIN SECTION
    # =====================================
    if user["role"] == "Admin":

        st.markdown("## 📁 Create Project")

        project_name = st.text_input("Project Name")

        project_description = st.text_area(
            "Description"
        )

        if st.button("Create Project"):

            result = create_project(
                project_name,
                project_description
            )

            st.success(result["message"])

        st.divider()

        st.markdown("## ➕ Create Task")

        task_title = st.text_input("Task Title")

        assigned_to = st.text_input(
            "Assign To Username"
        )

        deadline = st.date_input("Deadline")

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

                        update_task(
                            task["id"],
                            "Completed"
                        )

                        st.rerun()

                else:
                    st.success("Done")
```

---

# backend/requirements.txt

```txt
fastapi
uvicorn
pymongo
python-jose
passlib
bcrypt
pydantic
```

---

# frontend/requirements.txt

```txt
streamlit
requests
```

---

# RUN BACKEND

```bash
uvicorn main:app --reload
```

---

# RUN FRONTEND

```bash
streamlit run app.py
```

---

# OPEN URLS

Backend Docs:

```bash
http://127.0.0.1:8000/docs
```

Frontend:

```bash
http://localhost:8501
```

---

# DEPLOYMENT

## Backend

Deploy backend on:

* Railway
* Render

## Frontend

Deploy frontend on:

* Streamlit Cloud

Replace frontend BASE_URL with deployed Railway backend URL.
