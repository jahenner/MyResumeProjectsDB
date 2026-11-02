import unittest
import json
from datetime import date

# Import the classes from your src directory
from src.schema import Project, Challenge

class TestProjectSchema(unittest.TestCase):
    def setUp(self):
        """Set up a mock project payload before each test runs."""
        self.mock_project = Project(
            id="test-recon-01",
            title="Recon Dashboard",
            context="Personal",
            start_date=date(2026, 1, 15),
            end_date=None,
            summary="A test dashboard.",
            tools=["Python", "SQLite"],
            environment="Linux",
            challenges=[
                Challenge(issue="Memory leak", solution="Chunked data")
            ],
            repo_url="https://github.com/example/repo"
        )

    def test_to_dict_conversion(self):
        """Ensure the dataclass properly flattens to a dictionary."""
        data = self.mock_project.to_dict()
        self.assertEqual(data["id"], "test-recon-01")
        self.assertEqual(data["challenges"][0]["issue"], "Memory leak")

    def test_to_json_date_serialization(self):
        """Ensure datetime.date objects do not crash the JSON serializer."""
        json_str = self.mock_project.to_json()
        
        # Load it back into a dictionary to verify the string output
        parsed_data = json.loads(json_str)
        
        self.assertEqual(parsed_data["start_date"], "2026-01-15")
        self.assertIsNone(parsed_data["end_date"])

if __name__ == '__main__':
    unittest.main()