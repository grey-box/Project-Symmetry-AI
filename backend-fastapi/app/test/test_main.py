import pytest
from app.main import app

def test_app_exists():
    """Test that the FastAPI app can be imported"""
    assert app is not None

def test_app_has_title():
    """Test that the app has a title"""
    assert app.title is not None
    assert len(app.title) > 0

def test_app_has_version():
    """Test that the app has a version"""
    assert app.version is not None
    assert len(app.version) > 0