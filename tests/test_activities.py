import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: No setup needed, activities are pre-populated by fixture.
        Act: Send GET request to /activities endpoint.
        Assert: Verify response contains all activities with correct structure.
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 3
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_returns_correct_structure(self, client):
        """
        Arrange: No setup needed.
        Act: Send GET request and examine activity structure.
        Assert: Verify each activity has required fields.
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestRootRedirect:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_index_html(self, client):
        """
        Arrange: No setup needed.
        Act: Send GET request to root path with follow_redirects=False.
        Assert: Verify redirect status code and location.
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_successful_signup(self, client):
        """
        Arrange: Select an existing activity and new email.
        Act: Send POST request to signup endpoint.
        Assert: Verify success response and participant is added.
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "Signed up" in result["message"]
        assert new_email in result["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """
        Arrange: Get initial participant count.
        Act: Sign up a new student.
        Assert: Verify participant list is updated and count increases.
        """
        # Arrange
        activity_name = "Programming Class"
        new_email = "alex@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        client.post(f"/activities/{activity_name}/signup?email={new_email}")
        updated_response = client.get("/activities")

        # Assert
        updated_count = len(updated_response.json()[activity_name]["participants"])
        assert updated_count == initial_count + 1
        assert new_email in updated_response.json()[activity_name]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Use non-existent activity name.
        Act: Send signup request for invalid activity.
        Assert: Verify 404 error is returned with appropriate message.
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_student_returns_400(self, client):
        """
        Arrange: Use email already registered for activity.
        Act: Try to sign up same student twice.
        Assert: Verify 400 error is returned.
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )

        # Assert
        assert response.status_code == 400
        assert "Already signed up" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_successful_unregister(self, client):
        """
        Arrange: Select activity and participant to remove.
        Act: Send DELETE request to unregister.
        Assert: Verify success response.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "Unregistered" in result["message"]
        assert email in result["message"]

    def test_unregister_removes_participant(self, client):
        """
        Arrange: Get initial participant count.
        Act: Remove a participant.
        Assert: Verify participant is removed and count decreases.
        """
        # Arrange
        activity_name = "Gym Class"
        email_to_remove = "john@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        client.delete(f"/activities/{activity_name}/participants/{email_to_remove}")
        updated_response = client.get("/activities")

        # Assert
        updated_count = len(updated_response.json()[activity_name]["participants"])
        assert updated_count == initial_count - 1
        assert email_to_remove not in updated_response.json()[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Use non-existent activity name.
        Act: Send DELETE request for invalid activity.
        Assert: Verify 404 error is returned.
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_nonexistent_participant_returns_404(self, client):
        """
        Arrange: Use email not registered for activity.
        Act: Try to remove non-existent participant.
        Assert: Verify 404 error is returned.
        """
        # Arrange
        activity_name = "Programming Class"
        nonexistent_email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]
