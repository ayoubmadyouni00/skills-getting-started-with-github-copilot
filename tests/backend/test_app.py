from fastapi.testclient import TestClient
from src.app import app, activities


client = TestClient(app)


def ensure_participant(activity_name: str, email: str):
    participants = activities[activity_name]["participants"]
    if email not in participants:
        participants.append(email)


def remove_participant_if_exists(activity_name: str, email: str):
    participants = activities[activity_name]["participants"]
    if email in participants:
        participants.remove(email)


def test_root_redirect():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_and_remove_participant():
    name = "Chess Club"
    email = "teststudent@example.com"

    remove_participant_if_exists(name, email)

    resp = client.post(f"/activities/{name}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[name]["participants"]
    assert resp.json()["message"] == f"Signed up {email} for {name}"

    resp = client.delete(f"/activities/{name}/participants", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities[name]["participants"]
    assert resp.json()["message"] == f"Removed {email} from {name}"


def test_signup_fails_for_missing_activity():
    resp = client.post("/activities/UnknownClub/signup", params={"email": "missing@example.com"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"


def test_signup_fails_for_duplicate_participant():
    name = "Chess Club"
    email = "duplicate@example.com"

    ensure_participant(name, email)

    resp = client.post(f"/activities/{name}/signup", params={"email": email})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student already signed up"

    remove_participant_if_exists(name, email)


def test_remove_participant_fails_for_missing_activity():
    resp = client.delete("/activities/UnknownClub/participants", params={"email": "missing@example.com"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"


def test_remove_participant_fails_for_missing_participant():
    name = "Chess Club"
    email = "absent@example.com"

    remove_participant_if_exists(name, email)

    resp = client.delete(f"/activities/{name}/participants", params={"email": email})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Participant not found"
