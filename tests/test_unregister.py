"""
Unit tests for DELETE /activities/{activity_name}/unregister endpoint.

Tests cover the happy path, error cases, and edge cases for unregistering
students from activities.
"""

import pytest


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful_removes_participant(self, client):
        """Test successful unregistration removes email from participants."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

        # Verify participant was actually removed
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email not in participants

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test unregister from nonexistent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_unregistered_student_returns_400(self, client):
        """Test unregister of non-registered student returns 400."""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not registered for this activity" in response.json()["detail"]

    def test_unregister_then_signup_again_works(self, client):
        """Test that a student can unregister then sign up again."""
        # Arrange
        activity_name = "Chess Club"
        email = "flexible@mergington.edu"

        # Act - Initial signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert signup succeeded
        assert signup_response.status_code == 200

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert unregister succeeded
        assert unregister_response.status_code == 200

        # Act - Re-register
        ressignup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert re-registration succeeded
        assert ressignup_response.status_code == 200

        # Verify student is back in activity
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email in participants

    def test_unregister_multiple_times_fails_on_second_attempt(self, client):
        """Test that unregistering the same student twice fails on second attempt."""
        # Arrange
        activity_name = "Programming Class"
        email = "student@mergington.edu"

        # Act - First signup then unregister
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        first_unregister = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert first unregister succeeded
        assert first_unregister.status_code == 200

        # Act - Second unregister attempt
        second_unregister = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert second unregister fails
        assert second_unregister.status_code == 400
        assert "not registered for this activity" in second_unregister.json()["detail"]
