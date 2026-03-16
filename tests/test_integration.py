"""
Integration tests for multi-step workflows.

Tests verify that endpoints work together correctly in realistic scenarios,
testing the full signup/unregister lifecycle.
"""

import pytest


class TestActivityLifecycle:
    """Integration tests for activity signup/unregister workflows."""

    def test_signup_view_unregister_workflow(self, client):
        """Test complete workflow: signup → view in list → unregister → verify removal."""
        # Arrange
        activity_name = "Tennis Club"
        email = "athlete@mergington.edu"

        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert signup succeeded
        assert signup_response.status_code == 200

        # Act - View activities and verify participant is listed
        view_response = client.get("/activities")

        # Assert participant is visible
        assert view_response.status_code == 200
        participants = view_response.json()[activity_name]["participants"]
        assert email in participants
        initial_count = len(participants)

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert unregister succeeded
        assert unregister_response.status_code == 200

        # Act - View activities again verify participant is gone
        final_view_response = client.get("/activities")

        # Assert participant is no longer in list
        assert final_view_response.status_code == 200
        final_participants = final_view_response.json()[activity_name]["participants"]
        assert email not in final_participants
        assert len(final_participants) == initial_count - 1

    def test_multiple_students_signup_workflow(self, client):
        """Test that multiple students can sign up for the same activity."""
        # Arrange
        activity_name = "Drama Club"
        students = [
            "actor1@mergington.edu",
            "actor2@mergington.edu",
            "actor3@mergington.edu"
        ]

        # Act - Sign up multiple students
        signup_responses = []
        for email in students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            signup_responses.append(response)

        # Assert all signups succeeded
        for response in signup_responses:
            assert response.status_code == 200

        # Act - Verify all students are in participants list
        view_response = client.get("/activities")

        # Assert all students are present
        participants = view_response.json()[activity_name]["participants"]
        for email in students:
            assert email in participants

    def test_signup_unregister_signup_different_students(self, client):
        """Test that when one student unregisters, others remain and can re-signup."""
        # Arrange
        activity_name = "Art Studio"
        student1 = "artist1@mergington.edu"
        student2 = "artist2@mergington.edu"

        # Act - Both signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student1}
        )
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student2}
        )

        # Act - Student 1 unregisters
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student1}
        )

        # Assert unregister succeeded
        assert unregister_response.status_code == 200

        # Act - Verify student 2 is still there
        view_response = client.get("/activities")

        # Assert student 2 remains, student 1 is gone
        participants = view_response.json()[activity_name]["participants"]
        assert student1 not in participants
        assert student2 in participants

        # Act - Student 1 tries to signup again
        resignup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student1}
        )

        # Assert resignup succeeds
        assert resignup_response.status_code == 200

        # Act - Verify both are now in list
        final_view = client.get("/activities")

        # Assert both students are present
        final_participants = final_view.json()[activity_name]["participants"]
        assert student1 in final_participants
        assert student2 in final_participants
