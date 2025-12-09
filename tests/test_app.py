import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities before each test
    original = copy.deepcopy(app_module.activities)
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))
    yield
    # cleanup (not strictly necessary)
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))


def test_root_redirect():
    resp = client.get("/")
    assert resp.status_code == 307 or resp.status_code == 200


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    email = "newstudent@mergington.edu"
    resp = client.post(f"/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_already_signed():
    email = app_module.activities["Chess Club"]["participants"][0]
    resp = client.post(f"/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 400


def test_signup_activity_not_found():
    resp = client.post(f"/activities/NonExistent/signup", params={"email": "x@x.com"})
    assert resp.status_code == 404


def test_unregister_success():
    # Use an existing participant
    email = app_module.activities["Programming Class"]["participants"][0]
    resp = client.delete(f"/activities/Programming Class/participants", params={"email": email})
    assert resp.status_code == 200
    assert email not in app_module.activities["Programming Class"]["participants"]


def test_unregister_not_found_activity():
    resp = client.delete(f"/activities/Nope/participants", params={"email": "x@x.com"})
    assert resp.status_code == 404


def test_unregister_participant_not_in_activity():
    resp = client.delete(f"/activities/Chess Club/participants", params={"email": "not@there.com"})
    assert resp.status_code == 404
