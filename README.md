# MyResumeProjectsDB

A strictly-typed, zero-dependency project portfolio database and resume exporter built entirely with the Python 3 Standard Library. 

This tool is designed to securely log academic, personal, and professional projects, mapping them to specific tools and environments, and exporting them into a clean JSON format for automated resume builders.

## Architecture
* **Language:** Python 3 (Standard Library Only - no external requirements)
* **Backend:** Local SQLite (`sqlite3`) with strict foreign-key constraints
* **Data Modeling:** Native Python `dataclasses`
* **Interface:** Native `argparse` CLI wrapper (`./dossier`)
* **Testing:** Native `unittest` suite with in-memory database isolation

## Installation & Setup
### Clone the repository and initialize your environment:
```bash
git clone https://github.com/jahenner/MyResumeProjectsDB.git
cd MyResumeProjectsDB
```

### Create and activate the native virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Make the wrapper executable and initialize the database schema
```bash
chmod +x dossier
./dossier setup
```

## CLI Usage
Manage your portfolio via the interactive `./dossier` wrapper.

### 1. Populate Dependencies
Because the database is fully normalized, you must define contexts, environments, and tools before attaching them to a project.

```bash
./dossier add-context --id ctx-prof --name "Professional" --desc "Industry work"
./dossier add-environment --id env-linux --name "Kali VM" --desc "Kali Linux VM"
./dossier add-tool --id tool-py --name "Python 3" --desc "Primary Language"
```

#### View existing dependencies
```bash
./dossier list-contexts
./dossier list-environments
./dossier list-tools
```

### 2. Manage Projects
Add or update projects using the interactive wizard, which safely handles relational mapping and input validation.
```bash
./dossier add-project
./dossier list-projects
./dossier update-project --id "proj-1"
```

### 3. Safe Deletion
The CLI leverages SQLite `ON DELETE CASCADE` and blocks accidental deletion of dependencies currently in use.
```bash
./dossier delete project --id "proj-1"
./dossier delete tool --id "tool-py"
```

### 4. JSON Export
Export the relational database into a flat, denormalized JSON file ready for resume parsing.
```bash
./dossier export
```
Exports to `portfolio.json`

## Testing
Run the complete unit test suite (schema serialization and database operations):
```bash
python3 -m unittest discover -s tests -v
```

## License
[MIT License](LICENSE)