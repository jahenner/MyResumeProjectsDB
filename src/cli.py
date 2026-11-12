import argparse
import sqlite3
from datetime import date

from .db import PortfolioDB
from .schema import Project, Challenge, Context, Environment, Tool
from .export import export_portfolio_to_json

# --- Formatting Helpers ---
def print_table(headers, rows):
    """Prints data in a neat columnar format using standard f-strings."""
    if not rows:
        print("  (No entries found)\n")
        return
    print(f"  {headers[0]:<20} | {headers[1]}")
    print("  " + "-" * 50)
    for row in rows:
        print(f"  {row[0]:<20} | {row[1]}")
    print()

# --- Database Setup & Export ---
def setup_db(args):
    db = PortfolioDB()
    db.setup()
    print("[+] Database tables initialized successfully.")

def export_db(args):
    export_portfolio_to_json()
    print("[+] Exported portfolio to portfolio.json")

# --- Add Commands ---
def add_context(args):
    db = PortfolioDB()
    db.upsert_context(Context(id=args.id, name=args.name, description=args.desc))
    print(f"[+] Context '{args.name}' added successfully.")

def add_environment(args):
    db = PortfolioDB()
    db.upsert_environment(Environment(id=args.id, name=args.name, description=args.desc))
    print(f"[+] Environment '{args.name}' added successfully.")

def add_tool(args):
    db = PortfolioDB()
    db.upsert_tool(Tool(id=args.id, name=args.name, description=args.desc, doc_url=args.url))
    print(f"[+] Tool '{args.name}' added successfully.")

# --- List Commands ---
def list_contexts(args=None):
    db = PortfolioDB()
    print("\n--- Available Contexts ---")
    print_table(["Context ID", "Context Name"], db.get_all_contexts())

def list_environments(args=None):
    db = PortfolioDB()
    print("\n--- Available Environments ---")
    print_table(["Environment ID", "Environment Name"], db.get_all_environments())

def list_tools(args=None):
    db = PortfolioDB()
    print("\n--- Available Tools ---")
    print_table(["Tool ID", "Tool Name"], db.get_all_tools())
    
def list_projects(args=None):
    db = PortfolioDB()
    print("\n--- Available Projects ---")
    print_table(["Project ID", "Project Title"], db.get_all_projects())

# --- Interactive Project ---
def interactive_project(args):
    print("\n=== Add New Project (Interactive) ===")
    db = PortfolioDB()
    
    p_id = input("\nProject ID (e.g., proj-01): ").strip()
    title = input("Title: ").strip()
    
    # 1. Context Validation
    valid_contexts = {row[0] for row in db.get_all_contexts()}
    list_contexts()
    while True:
        context_id = input("Context ID (from above): ").strip()
        if context_id in valid_contexts:
            break
        print("[!] Invalid Context ID. Please try again.")
    
    # 2. Environment Validation
    valid_envs = {row[0] for row in db.get_all_environments()}
    list_environments()
    while True:
        env_id = input("Environment ID (from above): ").strip()
        if env_id in valid_envs:
            break
        print("[!] Invalid Environment ID. Please try again.")
    
    # 3. Dates (with optional end date)
    start_str = input("\nStart Date (YYYY-MM-DD): ").strip()
    start_parts = [int(x) for x in start_str.split("-")]
    
    end_str = input("End Date (YYYY-MM-DD, or press Enter to skip): ").strip()
    if end_str:
        end_parts = [int(x) for x in end_str.split("-")]
        end_date_obj = date(*end_parts)
    else:
        end_date_obj = None
    
    summary = input("Summary: ").strip()
    
    # 4. Tool Validation
    valid_tools = {row[0] for row in db.get_all_tools()}
    list_tools()
    while True:
        tools_input = input("Tool IDs (comma-separated, from above): ").strip()
        tool_ids = [t.strip() for t in tools_input.split(",") if t.strip()]
        
        invalid_tools = [t for t in tool_ids if t not in valid_tools]
        if not invalid_tools:
            break
        print(f"[!] Invalid Tool IDs found: {', '.join(invalid_tools)}. Please try again.")
    
    # 5. Challenges Loop
    print("\n--- Challenges ---")
    print("(Press Enter on 'Issue' without typing anything to finish adding challenges)")
    challenges_list = []
    while True:
        issue = input("\nWhat was the issue?: ").strip()
        if not issue:
            break  # Exit the loop if the user leaves it blank
        solution = input("How did you solve it?: ").strip()
        challenges_list.append(Challenge(issue=issue, solution=solution))
    
    repo_url = input("\nRepo URL (optional, press Enter to skip): ").strip()
    
    project = Project(
        id=p_id,
        title=title,
        context_id=context_id,
        environment_id=env_id,
        start_date=date(*start_parts),
        end_date=end_date_obj,
        summary=summary,
        tool_ids=tool_ids,
        challenges=challenges_list,
        repo_url=repo_url if repo_url else None
    )
    
    db.upsert_project(project)
    print(f"\n[+] Project '{title}' saved successfully.")
    
def update_project(args):
    db = PortfolioDB()
    proj = db.get_project(args.id)
    if not proj:
        print(f"[!] Project '{args.id}' not found.")
        return
        
    print(f"\n=== Update Project: {proj.title} ===")
    print("(Press Enter to keep the current value shown in brackets)")
    
    title = input(f"\nTitle [{proj.title}]: ").strip() or proj.title
    
    list_contexts()  # Inject context table
    valid_contexts = {row[0] for row in db.get_all_contexts()}
    while True:
        context_id = input(f"Context ID [{proj.context_id}]: ").strip() or proj.context_id
        if context_id in valid_contexts: break
        print("[!] Invalid Context ID.")

    list_environments()  # Inject environment table
    valid_envs = {row[0] for row in db.get_all_environments()}
    while True:
        env_id = input(f"Environment ID [{proj.environment_id}]: ").strip() or proj.environment_id
        if env_id in valid_envs: break
        print("[!] Invalid Environment ID.")

    start_str = input(f"\nStart Date [{proj.start_date.isoformat()}]: ").strip() or proj.start_date.isoformat()
    start_parts = [int(x) for x in start_str.split("-")]
    
    curr_end = proj.end_date.isoformat() if proj.end_date else "None"
    end_str = input(f"End Date [{curr_end}]: ").strip()
    end_str = end_str or curr_end
    end_date_obj = date(*[int(x) for x in end_str.split("-")]) if end_str != "None" else None

    summary = input(f"Summary [{proj.summary}]: ").strip() or proj.summary
    
    list_tools()  # Inject tool table
    curr_tools = ",".join(proj.tool_ids)
    valid_tools = {row[0] for row in db.get_all_tools()}
    while True:
        tools_input = input(f"Tool IDs [{curr_tools}]: ").strip() or curr_tools
        tool_ids = [t.strip() for t in tools_input.split(",") if t.strip()]
        invalid_tools = [t for t in tool_ids if t not in valid_tools]
        if not invalid_tools: break
        print(f"[!] Invalid Tool IDs: {', '.join(invalid_tools)}")

    print("\n[i] Challenges are overwritten entirely during an update.")
    keep_challs = input("Keep existing challenges? (Y/n): ").strip().lower()
    if keep_challs == 'n':
        challenges_list = []
        while True:
            issue = input("\nWhat was the issue? (Leave blank to stop): ").strip()
            if not issue: break
            solution = input("How did you solve it?: ").strip()
            challenges_list.append(Challenge(issue=issue, solution=solution))
    else:
        challenges_list = proj.challenges
        
    repo_url = input(f"Repo URL [{proj.repo_url or 'None'}]: ").strip()
    repo_url = repo_url if repo_url != "None" else None
    
    updated_proj = Project(
        id=proj.id, title=title, context_id=context_id, environment_id=env_id,
        start_date=date(*start_parts), end_date=end_date_obj, summary=summary,
        tool_ids=tool_ids, challenges=challenges_list, repo_url=repo_url
    )
    db.upsert_project(updated_proj)
    print(f"\n[+] Project '{proj.id}' updated successfully.")

def update_context(args):
    db = PortfolioDB()
    ctx = db.get_context(args.id)
    if not ctx:
        print(f"[!] Context '{args.id}' not found.")
        return
        
    print(f"\n=== Update Context: {ctx.name} ===")
    print("(Press Enter to keep the current value shown in brackets)")
    
    name = input(f"Name [{ctx.name}]: ").strip() or ctx.name
    desc = input(f"Description [{ctx.description}]: ").strip() or ctx.description
    
    db.upsert_context(Context(id=ctx.id, name=name, description=desc))
    print(f"[+] Context '{ctx.id}' updated successfully.")

def update_environment(args):
    db = PortfolioDB()
    env = db.get_environment(args.id)
    if not env:
        print(f"[!] Environment '{args.id}' not found.")
        return
        
    print(f"\n=== Update Environment: {env.name} ===")
    print("(Press Enter to keep the current value shown in brackets)")
    
    name = input(f"Name [{env.name}]: ").strip() or env.name
    desc = input(f"Description [{env.description}]: ").strip() or env.description
    
    db.upsert_environment(Environment(id=env.id, name=name, description=desc))
    print(f"[+] Environment '{env.id}' updated successfully.")

def update_tool(args):
    db = PortfolioDB()
    tool = db.get_tool(args.id)
    if not tool:
        print(f"[!] Tool '{args.id}' not found.")
        return
        
    print(f"\n=== Update Tool: {tool.name} ===")
    print("(Press Enter to keep the current value shown in brackets)")
    
    name = input(f"Name [{tool.name}]: ").strip() or tool.name
    desc = input(f"Description [{tool.description}]: ").strip() or tool.description
    
    curr_url = tool.doc_url or "None"
    url = input(f"Doc URL [{curr_url}]: ").strip() or curr_url
    url = url if url != "None" else None
    
    db.upsert_tool(Tool(id=tool.id, name=name, description=desc, doc_url=url))
    print(f"[+] Tool '{tool.id}' updated successfully.")

def delete_entity(args):
    db = PortfolioDB()
    try:
        if args.type == "project":
            if db.delete_project(args.id): print(f"[+] Project '{args.id}' deleted.")
            else: print(f"[!] Project '{args.id}' not found.")
        elif args.type == "context":
            db.delete_context(args.id)
            print(f"[+] Context '{args.id}' deleted.")
        elif args.type == "environment":
            db.delete_environment(args.id)
            print(f"[+] Environment '{args.id}' deleted.")
        elif args.type == "tool":
            db.delete_tool(args.id)
            print(f"[+] Tool '{args.id}' deleted.")
    except sqlite3.IntegrityError:
        print(f"[!] Cannot delete '{args.id}' because it is currently attached to a project.")
        print("    Reassign or delete the associated projects first.")

# --- Main Parser ---
def main():
    parser = argparse.ArgumentParser(description="MyResumeProjectsDB CLI Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    subparsers.add_parser("setup", help="Initialize the database tables")
    subparsers.add_parser("export", help="Export the database to JSON")
    subparsers.add_parser("add-project", help="Launch interactive prompt to add a project")
    
    # Add Commands
    ctx_parser = subparsers.add_parser("add-context", help="Add a new context")
    ctx_parser.add_argument("--id", required=True); ctx_parser.add_argument("--name", required=True); ctx_parser.add_argument("--desc", required=True)

    env_parser = subparsers.add_parser("add-environment", help="Add a new environment")
    env_parser.add_argument("--id", required=True); env_parser.add_argument("--name", required=True); env_parser.add_argument("--desc", required=True)

    tool_parser = subparsers.add_parser("add-tool", help="Add a new tool")
    tool_parser.add_argument("--id", required=True); tool_parser.add_argument("--name", required=True); tool_parser.add_argument("--desc", required=True); tool_parser.add_argument("--url", default=None)

    # List Commands
    subparsers.add_parser("list-contexts", help="View all contexts")
    subparsers.add_parser("list-environments", help="View all environments")
    subparsers.add_parser("list-tools", help="View all tools")
    subparsers.add_parser("list-projects", help="View all projects")
    
    # Update Project
    upd_proj_parser = subparsers.add_parser("update-project", help="Update an existing project interactively")
    upd_proj_parser.add_argument("--id", required=True, help="ID of the project to update")
    
    upd_ctx_parser = subparsers.add_parser("update-context", help="Update a context interactively")
    upd_ctx_parser.add_argument("--id", required=True)

    upd_env_parser = subparsers.add_parser("update-environment", help="Update an environment interactively")
    upd_env_parser.add_argument("--id", required=True)

    upd_tool_parser = subparsers.add_parser("update-tool", help="Update a tool interactively")
    upd_tool_parser.add_argument("--id", required=True)
    
    # Delete Commands
    delete_parser = subparsers.add_parser("delete", help="Delete an entity from the database")
    delete_parser.add_argument("type", choices=["project", "context", "environment", "tool"])
    delete_parser.add_argument("--id", required=True)

    args = parser.parse_args()

    commands = {
        "setup": setup_db, "export": export_db, "add-project": interactive_project,
        "add-context": add_context, "add-environment": add_environment, "add-tool": add_tool,
        "list-contexts": list_contexts, "list-environments": list_environments, "list-tools": list_tools,
        "update-project": update_project, "update-context": update_context, "update-environment": update_environment, "update-tool": update_tool,
        "delete": delete_entity, "list-projects": list_projects
    }
    commands[args.command](args)

if __name__ == "__main__":
    main()