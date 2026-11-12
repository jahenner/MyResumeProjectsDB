import unittest
import json
import tempfile
import os
from datetime import date

from src.schema import Project, Challenge, Context, Environment, Tool
from src.db import PortfolioDB

class TestPortfolioDB(unittest.TestCase):
    def setUp(self):
        """Create a temporary database file and normalized mock entities."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.test_dir.name, "test_portfolio.db")
        
        self.db = PortfolioDB(db_path=self.db_path)
        self.db.setup()
        
        # Setup dependencies required by foreign key constraints
        self.mock_context = Context(id="ctx-prof", name="Professional", description="Industry work")
        self.mock_env = Environment(id="env-kali", name="Kali VM", description="Offensive OS")
        self.mock_tool = Tool(id="tool-ghidra", name="Ghidra", description="RE Framework", doc_url=None)
        
        self.mock_project = Project(
            id="test-sec-01",
            title="Malware Triage Automator",
            context_id=self.mock_context.id,
            environment_id=self.mock_env.id,
            start_date=date(2025, 5, 10),
            end_date=None,
            summary="Automated reverse engineering pipeline.",
            tool_ids=[self.mock_tool.id],
            challenges=[
                Challenge(issue="Obfuscated payload", solution="Wrote an unpacking script")
            ],
            repo_url="https://github.com/example/malware-triage"
        )
        
    def tearDown(self):
        self.test_dir.cleanup()

    def test_table_creation(self):
        """Ensure the junction table and other tables are created successfully."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project_tools'")
            self.assertIsNotNone(cursor.fetchone())

    def test_upsert_inserts_new_project(self):
        """Ensure dependencies and projects are inserted and junction table maps correctly."""
        # Upsert dependencies first
        self.db.upsert_context(self.mock_context)
        self.db.upsert_environment(self.mock_env)
        self.db.upsert_tool(self.mock_tool)
        
        self.db.upsert_project(self.mock_project)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, challenges FROM projects WHERE id=?", (self.mock_project.id,))
            row = cursor.fetchone()
            
            self.assertIsNotNone(row)
            self.assertEqual(row[0], "Malware Triage Automator")
            self.assertEqual(json.loads(row[1])[0]["issue"], "Obfuscated payload")
            
            # Verify junction table mapping
            cursor.execute("SELECT tool_id FROM project_tools WHERE project_id=?", (self.mock_project.id,))
            tool_rows = cursor.fetchall()
            self.assertEqual(len(tool_rows), 1)
            self.assertEqual(tool_rows[0][0], self.mock_tool.id)

    def test_upsert_updates_existing_project(self):
        """Ensure upserting with an existing ID updates the row without foreign key errors."""
        self.db.upsert_context(self.mock_context)
        self.db.upsert_environment(self.mock_env)
        self.db.upsert_tool(self.mock_tool)
        
        self.db.upsert_project(self.mock_project)
        self.mock_project.title = "Updated Triage Automator"
        self.db.upsert_project(self.mock_project)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM projects WHERE id=?", (self.mock_project.id,))
            self.assertEqual(cursor.fetchone()[0], "Updated Triage Automator")

if __name__ == '__main__':
    unittest.main()