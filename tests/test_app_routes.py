def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    response = client.get("/activities")
    payload = response.json()

    assert response.status_code == 200
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"]
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_success_adds_participant(client):
    email = "new.student@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    updated = client.get("/activities").json()

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in updated["Chess Club"]["participants"]


def test_signup_unknown_activity_returns_404(client):
    response = client.post("/activities/Unknown%20Club/signup", params={"email": "a@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_400(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_url_encoded_activity_and_email(client):
    email = "first.last+robotics@mergington.edu"

    response = client.post(
        "/activities/Programming%20Class/signup",
        params={"email": email},
    )
    updated = client.get("/activities").json()

    assert response.status_code == 200
    assert email in updated["Programming Class"]["participants"]


def test_signup_only_mutates_targeted_activity(client):
    email = "isolation@mergington.edu"
    before = client.get("/activities").json()

    response = client.post("/activities/Math%20Club/signup", params={"email": email})
    after = client.get("/activities").json()

    assert response.status_code == 200
    assert email in after["Math Club"]["participants"]
    assert before["Chess Club"]["participants"] == after["Chess Club"]["participants"]


def test_unregister_success_removes_participant(client):
    email = "daniel@mergington.edu"

    response = client.delete("/activities/Chess%20Club/participants", params={"email": email})
    updated = client.get("/activities").json()

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in updated["Chess Club"]["participants"]


def test_unregister_unknown_activity_returns_404(client):
    response = client.delete(
        "/activities/Unknown%20Club/participants",
        params={"email": "someone@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_non_enrolled_student_returns_404(client):
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": "not.enrolled@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_url_encoded_email(client):
    email = "cleanup+tag@mergington.edu"
    client.post("/activities/Math%20Club/signup", params={"email": email})

    response = client.delete("/activities/Math%20Club/participants", params={"email": email})
    updated = client.get("/activities").json()

    assert response.status_code == 200
    assert email not in updated["Math Club"]["participants"]


def test_unregister_only_mutates_targeted_activity(client):
    before = client.get("/activities").json()

    response = client.delete(
        "/activities/Programming%20Class/participants",
        params={"email": "emma@mergington.edu"},
    )
    after = client.get("/activities").json()

    assert response.status_code == 200
    assert "emma@mergington.edu" not in after["Programming Class"]["participants"]
    assert before["Gym Class"]["participants"] == after["Gym Class"]["participants"]