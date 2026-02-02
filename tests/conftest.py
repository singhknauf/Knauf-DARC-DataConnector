"""
Test configuration and fixtures.
"""

import pytest
import os
from unittest.mock import MagicMock

# Add src to Python path for testing
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def mock_credential():
    """Mock Azure credential for testing."""
    mock_cred = MagicMock()
    mock_token = MagicMock()
    mock_token.token = "mock-token"
    mock_cred.get_token.return_value = mock_token
    return mock_cred


@pytest.fixture
def mock_connection():
    """Mock database connection for testing."""
    return MagicMock()