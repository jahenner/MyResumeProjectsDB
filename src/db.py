import sqlite3
import json
from dataclasses import asdict
from typing import List

from .schema import Project, Challenge

class PortfolioDB:
    def __init__(self, db_path: str = "portfolio.db"):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Creates and returns a database connection."""
        return sqlite3.connect(self.db_path)

    def setup(self) -> None:
        """Initializes the SQLite schema if it does not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    context TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    summary TEXT NOT NULL,
                    tools TEXT NOT NULL,       -- Stored as JSON string
                    environment TEXT NOT NULL,
                    challenges TEXT NOT NULL,  -- Stored as JSON string
                    repo_url TEXT
                )
            """)
            conn.commit()

    def upsert_project(self, project: Project) -> None:
        """Inserts a new project or updates an existing one based on ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Serialize Python lists/objects to JSON strings for SQLite storage
            tools_json = json.dumps(project.tools)
            challenges_json = json.dumps([asdict(c) for c in project.challenges])
            
            cursor.execute("""
                INSERT INTO projects (
                    id, title, context, start_date, end_date, 
                    summary, tools, environment, challenges, repo_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    context=excluded.context,
                    start_date=excluded.start_date,
                    end_date=excluded.end_date,
                    summary=excluded.summary,
                    tools=excluded.tools,
                    environment=excluded.environment,
                    challenges=excluded.challenges,
                    repo_url=excluded.repo_url
            """, (
                project.id,
                project.title,
                project.context,
                project.start_date.isoformat(),
                project.end_date.isoformat() if project.end_date else None,
                project.summary,
                tools_json,
                project.environment,
                challenges_json,
                project.repo_url
            ))
            conn.commit()