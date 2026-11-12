import argparse
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

    args = parser.parse_args()

    commands = {
        "setup": setup_db, "export": export_db, "add-project": interactive_project,
        "add-context": add_context, "add-environment": add_environment, "add-tool": add_tool,
        "list-contexts": list_contexts, "list-environments": list_environments, "list-tools": list_tools
    }
    commands[args.command](args)

if __name__ == "__main__":
    main()