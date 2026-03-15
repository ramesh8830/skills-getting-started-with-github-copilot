import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activity store between tests."""
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


@pytest.fixture
def client():
    """TestClient fixture for the FastAPI app."""
    return TestClient(app)


def test_get_activities(client):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert all(
        key in data["Chess Club"]
        for key in ["description", "schedule", "participants", "max_participants"]
    )


def test_signup_and_duplicate(client):
    # Arrange
    activity_name = "Chess Club"
    email = "test_student@mergington.edu"

    # Act (first signup)
    response1 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert (first signup succeeded)
    assert response1.status_code == 200

    # Act (duplicate signup)
    response2 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert (duplicate fails)
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_remove_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
