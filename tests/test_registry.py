import pytest
import sys
from unittest.mock import MagicMock, patch
from datetime import datetime

# Mock python-registry before importing the artifact module
mock_registry = MagicMock()

# Create a mock for RegistryKeyNotFoundException
class MockRegistryKeyNotFoundException(Exception):
    pass

# Set the exception on the mock module
mock_registry.RegistryKeyNotFoundException = MockRegistryKeyNotFoundException

sys.modules["Registry"] = mock_registry
sys.modules["Registry.Registry"] = mock_registry

from artifacts.registry import RegistryRunKeys

def test_registry_run_keys_extraction():
    # Setup
    hive_path = "test_hive.dat"
    
    # Mock os.path.exists
    with patch("os.path.exists", return_value=True):
        # Mock Registry.Registry construction
        mock_reg_obj = MagicMock()
        mock_registry.Registry.return_value = mock_reg_obj
        
        # Setup mock key
        mock_key = MagicMock()
        
        # Setup mock value
        mock_val = MagicMock()
        mock_val.name.return_value = "MaliciousUpdate"
        mock_val.value.return_value = "C:\\Windows\\Temp\\trojan.exe"
        mock_val.value_type_str.return_value = "RegSz"
        
        # Key has values
        mock_key.values.return_value = [mock_val]
        mock_key.timestamp.return_value = datetime(2023, 1, 1, 12, 0, 0)
        
        # Mock open to return the key for the first path and raise exception for others
        def mock_open(key_path):
            if key_path == "Microsoft\\Windows\\CurrentVersion\\Run":
                return mock_key
            raise MockRegistryKeyNotFoundException(f"Key not found: {key_path}")
        
        mock_reg_obj.open.side_effect = mock_open

        # Execute
        parser = RegistryRunKeys(hive_path)
        evidence = parser.extract()
        
        # Verify
        assert len(evidence) >= 1
        item = evidence[0]
        assert item.data["value_name"] == "MaliciousUpdate"
        assert item.data["value_data"] == "C:\\Windows\\Temp\\trojan.exe"
        assert item.artifact_type == "Registry Run Key"

def test_registry_file_not_found():
    parser = RegistryRunKeys("non_existent.dat")
    evidence = parser.extract()
    assert len(evidence) == 0
