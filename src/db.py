import sqlite3
import json
from dataclasses import asdict

from .schema import Project, Context, Tool, Environment

class PortfolioDB:
    def __init__(self, db_path: str = "portfolio.db"):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Creates a connection and strictly enforces foreign keys."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def setup(self) -> None:
        """Initializes the normalized relational schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contexts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS environments (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tools (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    doc_url TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    context_id TEXT NOT NULL,
                    environment_id TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    summary TEXT NOT NULL,
                    challenges TEXT NOT NULL,
                    repo_url TEXT,
                    FOREIGN KEY(context_id) REFERENCES contexts(id),
                    FOREIGN KEY(environment_id) REFERENCES environments(id)
                )
            """)
            
            # Junction table for the many-to-many Tools relationship
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_tools (
                    project_id TEXT NOT NULL,
                    tool_id TEXT NOT NULL,
                    PRIMARY KEY (project_id, tool_id),
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    FOREIGN KEY(tool_id) REFERENCES tools(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def upsert_context(self, ctx: Context) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO contexts (id, name, description) VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET name=excluded.name, description=excluded.description
            """, (ctx.id, ctx.name, ctx.description))

    def upsert_environment(self, env: Environment) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO environments (id, name, description) VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET name=excluded.name, description=excluded.description
            """, (env.id, env.name, env.description))

    def upsert_tool(self, tool: Tool) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO tools (id, name, description, doc_url) VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET name=excluded.name, description=excluded.description, doc_url=excluded.doc_url
            """, (tool.id, tool.name, tool.description, tool.doc_url))

    def upsert_project(self, project: Project) -> None:
        """Inserts the project and maps its tools in the junction table."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            challenges_json = json.dumps([asdict(c) for c in project.challenges])
            
            cursor.execute("""
                INSERT INTO projects (
                    id, title, context_id, environment_id, start_date, end_date, 
                    summary, challenges, repo_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    context_id=excluded.context_id,
                    environment_id=excluded.environment_id,
                    start_date=excluded.start_date,
                    end_date=excluded.end_date,
                    summary=excluded.summary,
                    challenges=excluded.challenges,
                    repo_url=excluded.repo_url
            """, (
                project.id, project.title, project.context_id, project.environment_id,
                project.start_date.isoformat(),
                project.end_date.isoformat() if project.end_date else None,
                project.summary, challenges_json, project.repo_url
            ))
            
            # Clear existing tool mappings to ensure a clean update
            cursor.execute("DELETE FROM project_tools WHERE project_id=?", (project.id,))
            
            for tool_id in project.tool_ids:
                cursor.execute("""
                    INSERT INTO project_tools (project_id, tool_id) VALUES (?, ?)
                """, (project.id, tool_id))
                
            conn.commit()