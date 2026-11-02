import unittest
import sqlite3
import json
import tempfile
import os
from datetime import date

from src.schema import Project, Challenge
from src.db import PortfolioDB

class TestPortfolioDB(unittest.TestCase):
    def setUp(self):
        """Create a temporary database file before every test."""
        # Create a secure temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.test_dir.name, "test_portfolio.db")
        
        self.db = PortfolioDB(db_path=self.db_path)
        self.db.setup()
        
        self.mock_project = Project(
            id="test-sec-01",
            title="Malware Triage Automator",
            context="Professional",
            start_date=date(2025, 5, 10),
            end_date=None,
            summary="Automated reverse engineering pipeline.",
            tools=["Python", "Ghidra", "Bash"],
            environment="Kali Linux VM",
            challenges=[
                Challenge(issue="Obfuscated payload", solution="Wrote an unpacking script")
            ],
            repo_url="https://github.com/example/malware-triage"
        )
        
    def tearDown(self):
        """Automatically delete the temporary database and directory after the test."""
        self.test_dir.cleanup()

    def test_table_creation(self):
        """Ensure the projects table is created successfully."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
            table_exists = cursor.fetchone()
            self.assertIsNotNone(table_exists)

    def test_upsert_inserts_new_project(self):
        """Ensure a new project is inserted and lists are serialized to JSON strings."""
        self.db.upsert_project(self.mock_project)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, tools, challenges FROM projects WHERE id=?", (self.mock_project.id,))
            row = cursor.fetchone()
            
            self.assertIsNotNone(row)
            self.assertEqual(row[0], "Malware Triage Automator")
            
            # Verify the JSON strings can be deserialized back into Python lists
            tools_list = json.loads(row[1])
            challenges_list = json.loads(row[2])
            
            self.assertIn("Ghidra", tools_list)
            self.assertEqual(challenges_list[0]["issue"], "Obfuscated payload")

    def test_upsert_updates_existing_project(self):
        """Ensure upserting with an existing ID updates the row instead of failing."""
        # 1. Initial insert
        self.db.upsert_project(self.mock_project)
        
        # 2. Modify object and update DB
        self.mock_project.title = "Updated Triage Automator"
        self.db.upsert_project(self.mock_project)
        
        # 3. Verify the change was saved
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM projects WHERE id=?", (self.mock_project.id,))
            row = cursor.fetchone()
            
            self.assertEqual(row[0], "Updated Triage Automator")

if __name__ == '__main__':
    unittest.main()