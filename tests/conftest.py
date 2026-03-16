"""
Pytest configuration and fixtures for FastAPI tests.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def clean_activities():
    """
    Arrange: Provide a clean copy of activities data for each test.
    Prevents test pollution by isolating state between tests.
    """
    return deepcopy(activities)


@pytest.fixture
def client(monkeypatch, clean_activities):
    """
    Arrange: Create a test client with isolated activities data.
    
    Uses monkeypatch to replace the global activities dict with a clean copy,
    ensuring each test starts with a known state.
    """
    monkeypatch.setattr("src.app.activities", clean_activities)
    return TestClient(app)
