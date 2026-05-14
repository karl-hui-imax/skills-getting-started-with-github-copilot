import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    """Reset mutable in-memory activities before every test."""
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)