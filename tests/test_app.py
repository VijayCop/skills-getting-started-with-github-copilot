import copy

from fastapi.testclient import TestClient
from src import app as app_module

client = TestClient(app_module.app)
initial_activities = copy.deepcopy(app_module.activities)


def setup_function() -> None:
    app_module.activities = copy.deepcopy(initial_activities)


def test_get_activities_returns_expected_data() -> None:
    # Arrange
    expected_activity_name = "Chess Club"

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity_name in payload
    assert isinstance(payload, dict)
    assert payload[expected_activity_name]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_participant() -> None:
    # Arrange
    activity_name = "Chess Club"
    new_email = "alexander@mergington.edu"
    expected_message = f"Signed up {new_email} for {activity_name}"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload["message"] == expected_message
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_for_unknown_activity_returns_404() -> None:
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Activity not found"


def test_signup_for_duplicate_participant_returns_400() -> None:
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": duplicate_email})
    payload = response.json()

    # Assert
    assert response.status_code == 400
    assert payload["detail"] == "Student is already signed up for this activity"


def test_remove_participant_removes_existing_student() -> None:
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    expected_message = f"Removed {existing_email} from {activity_name}"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": existing_email})
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload["message"] == expected_message
    assert existing_email not in app_module.activities[activity_name]["participants"]


def test_remove_participant_not_found_returns_404() -> None:
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": missing_email})
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Participant not found"
