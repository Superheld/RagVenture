# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RagVenture is a German-language text-based adventure game using Neo4j graph database for world state, Rich library for terminal UI, and following MVC architecture. The project is in Phase 1 (MVP Foundation) with plans to integrate LLM-based narration and NPCs in later phases.

**Tech Stack:** Python 3.10+, Neo4j (Docker), Rich Terminal UI, (future: Ollama for LLM integration)

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Neo4j Database
```bash
# Check if Neo4j container is running
docker ps | grep neo4j

# Start existing container (if stopped)
docker start textadv-dev

# Access Neo4j Browser
# URL: http://localhost:7474
# Credentials: neo4j / password (from .env)

# Reset database (WARNING: deletes all data)
# Run in Neo4j Browser: MATCH (n) DETACH DELETE n
# Then re-run notebooks/01-neo4j_dbsetup.ipynb
```

### Initialize World Data
```bash
# Start Jupyter and run setup notebook
jupyter notebook
# Open and execute: notebooks/01-neo4j_dbsetup.ipynb
# This creates schema constraints, indexes, and initial game world
```

### Run Game
```bash
python src/main.py
```

### Debug Database State
```bash
# Use the debug script to inspect current game state
python debug_db.py
```

## Architecture

### MVC Pattern
- **Model** (`src/model/game_model.py`): Neo4j database operations, all Cypher queries
- **View** (`src/view/game_view.py`): Rich terminal UI, display logic only
- **Controller** (`src/controller/game_controller.py`): Game loop, command routing, orchestration
- **Parser** (`src/utils/command_parser.py`): Simple text parser (returns `{action, targets, raw}`)

### Key Design Decisions

**Neo4j Graph Schema:**
- Nodes: `Player`, `Location`, `Item`, `NPC`
- Relationships: `IST_IN` (location/containment), `ERREICHT` (location connections), `TRÄGT` (player inventory)
- All IDs use German property names (e.g., `schluessel`, `taverne`)
- Player node always has ID `'player'` (not `'player_no1'`)

**Cypher Query Patterns:**
- Always use parameterized queries: `self._run_query(query, params={'key': value})`
- Model methods return lists of dicts from Neo4j results
- Use proper relationship directions: `(a)-[:REL]->(b)` matters
- Filter by node labels in WHERE when needed: `WHERE 'Item' IN labels(entity)`

**Command Processing Flow:**
```
User Input → Parser → Controller → Model → Neo4j → Model → Controller → View → Terminal
```

**Parser Output Format:**
```python
{
    'action': str,      # First word, lowercased
    'targets': list,    # Remaining words as list (empty if none)
    'raw': str         # Original input
}
```

### Current Game Commands
- `show location` - Current location details
- `show directions` - Available exits
- `show inventory` - Player's carried items
- `show content` - All entities at current location (Items + NPCs)
- `visit <location_id>` - Move to connected location (or list all if no target)
- `take <item_id>` - Pick up item (or list available items if no target)
- `drop <item_id>` - Drop item at current location (or show inventory if no target)
- `quit` - Exit game

## Git Workflow

**Branch Strategy:**
- `master` - main branch
- Feature branches for new functionality (e.g., `world-interactions`, `model`)
- **Always use `--no-ff` when merging** to preserve branch structure in git graph

```bash
# Merge with visible branch structure
git checkout master
git merge --no-ff feature-branch -m "Merge branch 'feature-branch' - Description"
```

**Commit Message Format:**
```
feat: Short description

Detailed explanation of changes:
- Bullet point 1
- Bullet point 2

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Important Context

### Language
- All code comments, documentation, and user-facing text are in **German**
- Variable names may be in English or German
- Neo4j property names are in German

### Database Connection
- Connection params come from `.env` file (not committed)
- Neo4j container name: `textadv-dev`
- Ports: 7474 (HTTP), 7687 (Bolt)
- Use `notifications_min_severity='OFF'` in driver config (optional, currently commented out)

### Common Patterns

**Adding a new Model method with Neo4j query:**
```python
def method_name(self, param):
    query = """
    MATCH (p:Player {id: 'player'})-[:IST_IN]->(loc:Location)
    MATCH (entity)-[:RELATIONSHIP]->(target)
    WHERE conditions
    RETURN entity.property
    """
    params = {'param': param}
    return self._run_query(query, params=params)
```

**Adding a new Controller command:**
```python
elif action == 'command':
    if not targets:
        # Show help/list
        result = self.model.list_method()
        self.view.show_list("Title", result)
        return
    else:
        # Execute command
        result = self.model.action_method(targets[0])
        if result:
            self.view.show_message(f'Success message')
```

### Known Gotchas

1. **Parser returns `targets` as list** - Use `targets[0]` when passing to Model methods expecting a string
2. **Python dict vs set syntax** - `{'key': value}` not `{'key', value}`
3. **Relationship directions matter** - `(a)-[:REL]->(b)` is different from `(a)<-[:REL]-(b)`
4. **Cache issues** - Restart `python src/main.py` after code changes (Python caches modules)
5. **Label filtering** - Use `:Item` in MATCH or `WHERE 'Item' IN labels(entity)` to filter node types

## Documentation

- `docs/neo4j_cheatsheet.md` - Comprehensive Cypher WHERE clause reference
- `docs/architecture_idea.md` - Original architecture vision (for reference, may differ from current state)
- `docs/neo4j_docker.md` - Docker setup details
- `README.md` - Setup instructions and roadmap
- `notebooks/01-neo4j_dbsetup.ipynb` - Database initialization (run this first!)
- `notebooks/02-neo4j_commands.ipynb` - Query testing and experimentation

## Future Roadmap Context

The codebase is designed to eventually support:
- LLM-based narrator (Ollama integration)
- NPC personalities with individual prompts
- Natural language parser (replacing current keyword parser)
- Command Pattern refactoring (currently flat if/elif in Controller)

When making changes, keep extensibility in mind but don't over-engineer for future phases.
