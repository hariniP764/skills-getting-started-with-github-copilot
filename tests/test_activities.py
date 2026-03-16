"""
Unit tests for GET /activities endpoint.

Tests verify that activities are retrieved correctly with proper structure
and participant information.
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities."""
        # Arrange
        # (client fixture provides clean activities data)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_includes_activity_details(self, client):
        """Test that each activity has required fields."""
        # Arrange
        # (client fixture provides clean activities data)

        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club

    def test_get_activities_includes_initial_participants(self, client):
        """Test that activities include their initial participants."""
        # Arrange
        # (client fixture provides clean activities data)

        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        chess_club_participants = data["Chess Club"]["participants"]
        
        assert "michael@mergington.edu" in chess_club_participants
        assert "daniel@mergington.edu" in chess_club_participants
        assert len(chess_club_participants) == 2
