"""
Unit tests for POST /activities/{activity_name}/signup endpoint.

Tests cover the happy path, error cases, and edge cases including
the duplicate signup bug fix.
"""

import pytest


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful_adds_participant(self, client):
        """Test successful signup adds email to participants."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was actually added
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email in participants

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test signup to nonexistent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_returns_400(self, client):
        """Test that signing up for same activity twice returns 400 (bug fix test)."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "Already signed up for this activity" in response.json()["detail"]

    def test_signup_prevents_multiple_registrations_by_same_student(self, client):
        """Test that a student cannot register multiple times for the same activity."""
        # Arrange
        activity_name = "Programming Class"
        email = "testuser@mergington.edu"

        # Act - First signup
        first_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert first signup succeeds
        assert first_response.status_code == 200

        # Act - Second signup attempt
        second_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert second signup fails
        assert second_response.status_code == 400
        assert "Already signed up" in second_response.json()["detail"]

    def test_signup_same_student_different_activities_allowed(self, client):
        """Test that a student can sign up for different activities."""
        # Arrange
        email = "flexible_student@mergington.edu"

        # Act - Sign up for Chess Club
        chess_response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )

        # Act - Sign up for Programming Class
        programming_response = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )

        # Assert both signups succeeded
        assert chess_response.status_code == 200
        assert programming_response.status_code == 200

        # Verify student is in both activities
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]
