import pytest
from core.artifact import Artifact, Evidence
from datetime import datetime

class MockArtifact(Artifact):
    @property
    def name(self):
        return "Mock Artifact"
    
    @property
    def description(self):
        return "Used for testing"
    
    def extract(self):
        return [
            Evidence(
                source_path="/tmp/test",
                artifact_type="mock",
                data={"foo": "bar"},
                timestamp=datetime.now()
            )
        ]

def test_artifact_interface():
    """
    Ensure the MockArtifact adheres to the Abstract Base Class logic.
    """
    a = MockArtifact()
    assert a.name == "Mock Artifact"
    results = a.extract()
    assert len(results) == 1
    assert results[0].data["foo"] == "bar"
