import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Initial state of activities for resetting between tests
INITIAL_ACTIVITIES = {
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
    "Basketball Team": {
        "description": "Practice and compete in basketball games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Soccer Club": {
        "description": "Train and play soccer matches",
        "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
        "max_participants": 22,
        "participants": []
    },
    "Art Club": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "Drama Club": {
        "description": "Act in plays and learn theater skills",
        "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Debate Club": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": []
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": []
    }
}


@pytest.fixture
def client():
    # Reset activities to initial state
    activities.clear()
    activities.update(INITIAL_ACTIVITIES)
    # Create TestClient
    test_client = TestClient(app, follow_redirects=False)
    return test_client


def test_root_redirect(client):
    # Arrange - client fixture provides TestClient
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    # Arrange - client fixture provides TestClient
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Verify structure
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "test@example.com"
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert f"Signed up {email} for {activity_name}" in response.json()["message"]
    # Verify participant added
    response2 = client.get("/activities")
    data = response2.json()
    assert email in data[activity_name]["participants"]


def test_signup_activity_not_found(client):
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test@example.com"
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_already_signed_up(client):
    # Arrange
    activity_name = "Chess Club"
    email = "test@example.com"
    # First signup
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Act - second signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400
    assert "Student already signed up" in response.json()["detail"]


def test_remove_participant_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "test@example.com"
    # Signup first
    client.post(f"/activities/{activity_name}/signup", json={"email": email})
    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    # Assert
    assert response.status_code == 200
    assert f"Removed {email} from {activity_name}" in response.json()["message"]
    # Verify participant removed
    response2 = client.get("/activities")
    data = response2.json()
    assert email not in data[activity_name]["participants"]


def test_remove_participant_activity_not_found(client):
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test@example.com"
    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_remove_participant_not_found(client):
    # Arrange
    activity_name = "Chess Club"
    email = "nonexistent@example.com"
    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    # Assert
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]