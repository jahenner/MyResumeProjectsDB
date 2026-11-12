import unittest
import tempfile
import os
import json
from datetime import date

from src.schema import Project, Context, Environment, Tool
from src.db import PortfolioDB
from src.export import export_portfolio_to_json

class TestExportLogic(unittest.TestCase):
    def setUp(self):
        # Setup isolated environment
        self.test_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.test_dir.name, "test.db")
        self.json_path = os.path.join(self.test_dir.name, "output.json")
        
        # Populate data
        db = PortfolioDB(self.db_path)
        db.setup()
        db.upsert_context(Context("ctx-1", "Academic", "University work"))
        db.upsert_environment(Environment("env-1", "Ubuntu 22.04", "Linux"))
        db.upsert_tool(Tool("tool-1", "Python 3", "Language", None))
        db.upsert_tool(Tool("tool-2", "Streamlit", "UI", None))
        
        proj = Project(
            id="proj-1", title="Test App", context_id="ctx-1", environment_id="env-1",
            start_date=date(2026, 8, 1), end_date=None, summary="Test summary",
            tool_ids=["tool-1", "tool-2"], challenges=[], repo_url=None
        )
        db.upsert_project(proj)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_json_export_denormalization(self):
        """Ensure IDs are converted to readable names in the final JSON."""
        export_portfolio_to_json(self.db_path, self.json_path)
        
        self.assertTrue(os.path.exists(self.json_path))
        
        with open(self.json_path, 'r') as f:
            data = json.load(f)
            
        project = data["resume_projects"][0]
        
        # Verify the IDs were replaced with the human-readable names
        self.assertEqual(project["context"], "Academic")
        self.assertEqual(project["environment"], "Ubuntu 22.04")
        self.assertIn("Python 3", project["tools"])
        self.assertIn("Streamlit", project["tools"])

if __name__ == '__main__':
    unittest.main()