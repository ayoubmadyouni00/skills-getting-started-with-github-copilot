from fastapi.testclient import TestClient
from src.app import app, activities


client = TestClient(app)


def test_root_redirect():
    resp = client.get("/")
    assert resp.status_code == 200
    # index.html is served from the static mount; ensure content is HTML
    assert "text/html" in resp.headers["content-type"]


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)


def test_signup_and_remove_participant():
    name = "Chess Club"
    email = "teststudent@example.com"

    # Ensure not already in participants
    if email in activities[name]["participants"]:
        activities[name]["participants"].remove(email)

    # Signup
    resp = client.post(f"/activities/{name}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[name]["participants"]

    # Remove
    resp = client.delete(f"/activities/{name}/participants", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities[name]["participants"]
