import json

from .db import PortfolioDB

def export_portfolio_to_json(db_path: str = "portfolio.db", output_file: str = "portfolio.json") -> None:
    """Denormalizes the SQLite database and exports it to a resume-ready JSON file."""
    db = PortfolioDB(db_path)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Fetch lookups to resolve foreign keys
        cursor.execute("SELECT id, name FROM contexts")
        contexts = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id, name FROM environments")
        environments = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id, name FROM tools")
        tools = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Fetch projects
        cursor.execute("""
            SELECT id, title, context_id, environment_id, start_date, end_date, summary, challenges, repo_url 
            FROM projects
        """)
        
        projects_payload = []
        for row in cursor.fetchall():
            proj_id, title, ctx_id, env_id, start, end, summary, challenges_json, repo = row
            
            # Fetch mapped tool IDs from junction table
            cursor.execute("SELECT tool_id FROM project_tools WHERE project_id=?", (proj_id,))
            mapped_tool_ids = [t_row[0] for t_row in cursor.fetchall()]
            
            project_data = {
                "id": proj_id,
                "title": title,
                "context": contexts.get(ctx_id, "Unknown Context"),
                "environment": environments.get(env_id, "Unknown Environment"),
                "start_date": start,
                "end_date": end,
                "summary": summary,
                "tools": [tools.get(tid, tid) for tid in mapped_tool_ids],
                "challenges": json.loads(challenges_json),
                "repo_url": repo
            }
            projects_payload.append(project_data)
            
        export_document = {
            "metadata": {
                "format": "DevDossier-v1",
                "exported_records": len(projects_payload)
            },
            "resume_projects": projects_payload
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_document, f, indent=2)