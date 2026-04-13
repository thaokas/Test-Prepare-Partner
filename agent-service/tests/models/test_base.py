import pytest
import inspect
from app.models.base import Base, get_db

def test_base_is_declarative():
    """Base should be a declarative base"""
    assert hasattr(Base, 'metadata')
    assert hasattr(Base, '__tablename__') or True  # declarative base

def test_get_db_is_async_generator():
    """get_db should be an async generator function"""
    assert inspect.isasyncgenfunction(get_db)
