"""High School Management System API."""

import os
from pathlib import Path
from typing import Dict, Literal, Optional, Set
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(
    title="Mergington High School API",
    description=(
        "API for viewing activities, authentication, and club membership "
        "management"
    ),
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


clubs = {
    "Chess Club": {
        "description": "Strategy, tactics, and friendly weekly competition"
    },
    "Programming Club": {
        "description": "Build coding projects, games, and practical tools"
    },
    "Soccer Club": {
        "description": "Weekly football training and inter-school matches"
    },
    "Art Club": {
        "description": "Painting, drawing, and collaborative design"
    },
    "Drama Club": {
        "description": "Acting workshops and school-stage performances"
    },
    "Debate Club": {
        "description": "Public speaking and argumentation practice"
    },
}


RoleType = Literal["user", "admin", "super_admin"]


class UserRecord(BaseModel):
    email: str
    password: str
    role: RoleType = "user"
    memberships: Set[str] = set()


class RegisterRequest(BaseModel):
    email: str
    password: str
    role: RoleType = "user"


class LoginRequest(BaseModel):
    email: str
    password: str


users: Dict[str, UserRecord] = {
    "admin@mergington.edu": UserRecord(
        email="admin@mergington.edu",
        password="admin123",
        role="admin",
        memberships={"Programming Club"},
    ),
    "student@mergington.edu": UserRecord(
        email="student@mergington.edu",
        password="student123",
        role="user",
        memberships={"Chess Club"},
    ),
}

sessions: Dict[str, str] = {}


def get_current_user(authorization: Optional[str]) -> UserRecord:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ", 1)[1].strip()
    email = sessions.get(token)
    if not email or email not in users:
        raise HTTPException(status_code=401, detail="Session is invalid or expired")

    return users[email]


def normalize_and_validate_email(value: str) -> str:
    normalized = value.strip().lower()
    if "@" not in normalized or "." not in normalized.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Invalid email format")
    return normalized


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/auth/register")
def register(payload: RegisterRequest):
    email = normalize_and_validate_email(payload.email)
    if email in users:
        raise HTTPException(status_code=400, detail="Email already registered")

    users[email] = UserRecord(
        email=email,
        password=payload.password,
        role=payload.role,
        memberships=set(),
    )

    return {
        "message": "Registration successful",
        "user": {
            "email": email,
            "role": payload.role,
        },
    }


@app.post("/auth/login")
def login(payload: LoginRequest):
    email = normalize_and_validate_email(payload.email)
    user = users.get(email)
    if not user or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = str(uuid4())
    sessions[token] = email

    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "email": user.email,
            "role": user.role,
            "memberships": sorted(user.memberships),
        },
    }


@app.post("/auth/logout")
def logout(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ", 1)[1].strip()
    sessions.pop(token, None)
    return {"message": "Logout successful"}


@app.get("/auth/me")
def me(authorization: Optional[str] = Header(default=None)):
    user = get_current_user(authorization)
    return {
        "email": user.email,
        "role": user.role,
        "memberships": sorted(user.memberships),
    }


@app.get("/clubs")
def get_clubs(authorization: Optional[str] = Header(default=None)):
    user = get_current_user(authorization)
    return {
        name: {
            "description": data["description"],
            "membership_state": "Joined" if name in user.memberships else "Join",
        }
        for name, data in clubs.items()
    }


@app.get("/memberships")
def get_memberships(authorization: Optional[str] = Header(default=None)):
    user = get_current_user(authorization)
    return {"memberships": sorted(user.memberships)}


@app.post("/clubs/{club_name}/join")
def join_club(club_name: str, authorization: Optional[str] = Header(default=None)):
    user = get_current_user(authorization)
    if club_name not in clubs:
        raise HTTPException(status_code=404, detail="Club not found")

    if club_name in user.memberships:
        return {
            "message": f"Already joined {club_name}",
            "membership_state": "Joined",
        }

    user.memberships.add(club_name)
    return {
        "message": f"Joined {club_name}",
        "membership_state": "Joined",
    }


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(
    activity_name: str,
    authorization: Optional[str] = Header(default=None),
):
    """Sign up a student for an activity"""
    user = get_current_user(authorization)

    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if user.email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(user.email)
    return {"message": f"Signed up {user.email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(
    activity_name: str,
    authorization: Optional[str] = Header(default=None),
):
    """Unregister a student from an activity"""
    user = get_current_user(authorization)

    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if user.email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(user.email)
    return {"message": f"Unregistered {user.email} from {activity_name}"}
