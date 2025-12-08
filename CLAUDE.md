# CLAUDE.md - RagVenture AI Assistant Guide

**Last Updated:** December 8, 2025
**Project:** RagVenture - AI-Enhanced Text Adventure Game
**Tech Stack:** Python 3.10+, Neo4j Graph Database, Rich Terminal UI

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design Patterns](#architecture--design-patterns)
3. [Codebase Structure](#codebase-structure)
4. [Development Workflows](#development-workflows)
5. [Coding Conventions](#coding-conventions)
6. [Neo4j Graph Database](#neo4j-graph-database)
7. [Common Development Tasks](#common-development-tasks)
8. [Known Issues & Constraints](#known-issues--constraints)
9. [Testing Strategy](#testing-strategy)
10. [Future Roadmap Context](#future-roadmap-context)

---

## 🎮 Project Overview

### What is RagVenture?

RagVenture is a text-based adventure game that combines traditional text adventure mechanics with modern AI capabilities. The project serves as both a playable game and a learning platform for:

- Graph database modeling (Neo4j)
- MVC architecture patterns
- Terminal UI development (Rich library)
- Future AI/LLM integration (Ollama, LangChain)
- Procedural content generation

### Current Development Phase

**Phase 1 MVP (Week 1)** - Nearly Complete
- ✅ Core MVC architecture
- ✅ Player movement system
- ✅ Item pickup/drop mechanics
- ✅ Neo4j graph database integration
- ✅ Rich terminal UI foundation
- ⚠️ Has known syntax errors requiring fixes

### Project Goals

1. **Educational:** Learn graph databases, AI integration, and game development
2. **Extensible:** Modular design ready for AI narrator, NPC dialogs, and procedural generation
3. **Professional:** Demonstrate clean architecture and software engineering practices

---

## 🏗️ Architecture & Design Patterns

### MVC Pattern Implementation

RagVenture follows a strict Model-View-Controller separation:

```
┌─────────────────────────────────────────┐
│         GameController                  │
│  • Routes commands                      │
│  • Orchestrates game loop               │
│  • Validates input                      │
└────┬─────────────────────────┬──────────┘
     │                         │
     ▼                         ▼
┌──────────────┐        ┌──────────────┐
│  GameModel   │        │  GameView    │
│  • Neo4j ops │        │  • Rich UI   │
│  • Data layer│        │  • Display   │
└──────────────┘        └──────────────┘
     │
     ▼                  ┌──────────────┐
┌──────────────┐        │CommandParser │
│  Neo4j DB    │        │  • Parsing   │
└──────────────┘        └──────────────┘
```

### Design Patterns Used

| Pattern | Implementation | Purpose |
|---------|---------------|---------|
| **Repository** | `GameModel` class | Abstracts Neo4j database operations |
| **Command** | Parsed command dicts | Encapsulates user actions |
| **Facade** | `GameController` | Simplifies component interactions |
| **Dependency Injection** | Constructor-based | Loose coupling between components |

### Key Architectural Principles

1. **Separation of Concerns:** Each layer has single responsibility
2. **No Direct DB Access:** Only `GameModel` talks to Neo4j
3. **Stateless Components:** Game state lives in database only
4. **Loose Coupling:** Components interact through defined interfaces

---

## 📁 Codebase Structure

### Directory Layout

```
RagVenture/
├── src/                          # Application source code (278 LOC)
│   ├── main.py                   # Entry point (7 lines)
│   ├── controller/
│   │   └── game_controller.py    # Game loop & command routing (100 lines)
│   ├── model/
│   │   ├── game_model.py         # Neo4j operations (121 lines)
│   │   └── game_init.cypher      # Database initialization queries
│   ├── view/
│   │   └── game_view.py          # Rich terminal UI (35 lines)
│   └── utils/
│       └── command_parser.py     # Command parsing (19 lines)
├── notebooks/                    # Jupyter development notebooks
│   ├── 01-neo4j_dbsetup.ipynb   # Schema & world initialization
│   └── 02-neo4j_commands.ipynb   # Query testing & exploration
├── docs/                         # Documentation
│   ├── architecture_idea.md      # MVC design decisions
│   ├── neo4j_cheatsheet.md       # Cypher syntax reference
│   └── neo4j_docker.md           # Docker setup guide
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # Project setup guide
```

### Core Components

#### 1. **Entry Point** (`src/main.py`)

```python
from controller.game_controller import GameController

def main():
    controller = GameController()
    controller.run_game()
```

**Purpose:** Simple bootstrapper that starts the game loop

---

#### 2. **Game Controller** (`src/controller/game_controller.py`)

**Responsibilities:**
- Initialize Model, View, and Parser components
- Run the main game loop
- Process and route commands
- Validate command targets

**Supported Commands:**
| Command | Parameters | Action |
|---------|-----------|--------|
| `quit` | None | Exits game |
| `show inventory` | None | Display carried items |
| `show location` | None | Display current room |
| `show directions` | None | Display reachable locations |
| `show content` | None | Display items in current room |
| `visit <location_id>` | Location ID | Move player |
| `take <item_id>` | Item ID | Pickup item |
| `drop <item_id>` | Item ID | Drop item |

**Command Flow:**
```python
User Input → Parser.parse() → GameController.process_command()
    ↓
Route by action → Call appropriate model method
    ↓
Get result → Call view.show_*() → Terminal output
```

---

#### 3. **Game Model** (`src/model/game_model.py`)

**Responsibilities:**
- Manage Neo4j driver connection
- Execute parameterized Cypher queries
- Return query results as Python dicts

**Key Methods:**

| Method | Returns | Cypher Pattern |
|--------|---------|---------------|
| `current_location()` | Player's current location | `MATCH (p:Player)-[:IST_IN]->(loc)` |
| `location_content()` | Items in current room | `MATCH (item)-[:IST_IN]->(loc)` |
| `location_connections()` | Adjacent locations | `MATCH (loc)-[:ERREICHT]->(target)` |
| `player_inventory()` | Carried items | `MATCH (p)-[:TRÄGT]->(item)` |
| `move_player(to_loc)` | New location info | DELETE/CREATE `:IST_IN` relationship |
| `take_item(item_id)` | Item details | DELETE `:IST_IN`, CREATE `:TRÄGT` |
| `drop_item(item_id)` | Drop confirmation | DELETE `:TRÄGT`, CREATE `:IST_IN` |
| `use_item(item_id)` | Placeholder | Not yet implemented |

**Neo4j Connection:**
```python
# Loads from .env file
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

self.driver = GraphDatabase.driver(NEO4J_URI, auth=(user, password))
```

---

#### 4. **Game View** (`src/view/game_view.py`)

**Responsibilities:**
- Display formatted output using Rich library
- Collect user input
- Handle empty states

**Rich Components:**
- `Console` - Main output handler
- `Panel` - Styled containers (welcome screen)
- `Prompt` - User input collection

**Methods:**
| Method | Purpose | Output Style |
|--------|---------|-------------|
| `show_welcome()` | Display title screen | Yellow-bordered Panel |
| `get_command()` | Collect user input | Rich Prompt |
| `show_message(text)` | Display single message | Prefixed with "Antwort: " |
| `show_list(items)` | Display collections | Dim styling for empty |

---

#### 5. **Command Parser** (`src/utils/command_parser.py`)

**Current Implementation:** Simple word splitting

```python
def parse(self, input_text):
    words = input_text.lower().strip().split()
    return {
        'action': words[0],       # First word (verb)
        'targets': words[1:],     # Remaining words (objects)
        'raw': input_text         # Original input
    }
```

**Limitations:**
- No synonym resolution
- No stopword removal
- No multi-word entity support
- No validation

**Future Enhancement (Phase 4):**
- Natural language understanding with LLM
- Fuzzy matching for entity names
- Synonym handling
- Disambiguation prompts

---

## 🔄 Development Workflows

### Environment Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd RagVenture

# 2. Create virtual environment
python -m venv venv

# 3. Activate environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env with Neo4j credentials:
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=password
```

### Neo4j Docker Setup

```bash
# Start Neo4j container
docker run -d \
    --name textadventure-neo4j \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    -v neo4j_data:/data \
    neo4j:latest

# Verify container is running
docker ps | grep textadventure-neo4j

# Access Neo4j Browser
# Open http://localhost:7474
# Login: neo4j / password
```

### Database Initialization

```bash
# Start Jupyter
jupyter notebook

# Run notebooks in order:
# 1. notebooks/01-neo4j_dbsetup.ipynb
#    - Creates constraints and indexes
#    - Generates initial game world
#    - Creates player, locations, items, NPCs

# 2. notebooks/02-neo4j_commands.ipynb (optional)
#    - Test Cypher queries
#    - Explore database structure
```

### Running the Game

```bash
# Ensure virtual environment is active
source venv/bin/activate

# Start game
python src/main.py
```

### Git Workflow

**Branch Naming Convention:**
- Feature branches: `claude/claude-<feature>-<session-id>`
- Always push to the designated branch
- Never push to main/master without explicit permission

**Commit Message Style:**
```
feat: Add item pickup functionality
fix: Resolve f-string syntax error in controller
docs: Update Neo4j cheatsheet with new queries
update: Enhance player movement validation
```

**Common Git Operations:**
```bash
# Check current branch and status
git status

# Create and switch to new branch
git checkout -b feature/your-feature-name

# Stage and commit changes
git add <files>
git commit -m "feat: Your descriptive message"

# Push to remote (with retry logic for network issues)
git push -u origin <branch-name>
```

---

## 📐 Coding Conventions

### Naming Standards

| Element | Convention | Example |
|---------|-----------|---------|
| Classes | PascalCase | `GameController`, `GameModel` |
| Functions/Methods | snake_case | `run_game`, `process_command` |
| Private Methods | Leading underscore | `_run_query` |
| Variables | snake_case | `player_id`, `current_location` |
| Constants | UPPER_SNAKE_CASE | `NEO4J_URI` (in future) |
| Database IDs | lowercase_underscore | `forest_entrance`, `item_sword` |

### Language Usage

**Hybrid German/English:**
- **Code:** English (classes, methods, variables)
- **UI Messages:** German (user-facing text)
- **Comments:** German
- **Database Relationships:** German (`IST_IN`, `TRÄGT`, `ERREICHT`)

**Rationale:** English for code readability, German for immersive gameplay

### File Organization

**Import Order:**
1. Standard library imports
2. Third-party imports (neo4j, rich, dotenv)
3. Local imports (relative imports)

**Example:**
```python
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from view.game_view import GameView
```

### Code Style

- **Indentation:** 4 spaces (no tabs)
- **Line Length:** No strict limit (keep reasonable)
- **Comments:** Minimal - prefer self-documenting code
- **Docstrings:** Optional - only for complex methods
- **Type Hints:** Not currently used (consider for future)

### Error Handling Pattern

**Current State:** Minimal error handling

**Expected Pattern (for future):**
```python
# Validate inputs early
if not targets:
    self.view.show_message('Error message')
    return

# Check operation results
result = self.model.some_operation()
if not result:
    self.view.show_message('Operation failed')
    return

# Success path
self.view.show_success(result)
```

**Areas Needing Error Handling:**
- Neo4j connection failures
- Query execution errors
- Invalid item/location IDs
- Empty result sets
- Database constraint violations

---

## 🗄️ Neo4j Graph Database

### Schema Overview

#### Node Labels

| Label | Purpose | Properties |
|-------|---------|-----------|
| `Player` | Game protagonist | `id` (string), `name` (optional) |
| `Location` | Rooms/areas | `id`, `name`, `description` |
| `Item` | Collectible objects | `id`, `name`, `description` |
| `NPC` | Non-player characters | `id`, `name`, `dialogue` (future) |

#### Relationship Types

| Type | Pattern | Purpose | Example |
|------|---------|---------|---------|
| `IST_IN` | `(Entity)-[:IST_IN]->(Location)` | Entity location | Player in Room |
| `TRÄGT` | `(Player)-[:TRÄGT]->(Item)` | Player inventory | Player carries Sword |
| `ERREICHT` | `(Location)-[:ERREICHT]->(Location)` | Movement graph | Room connects to Room |

**Future Relationships (Roadmap):**
- `WANTS` / `GIVES` - NPC quest system
- `LOCKED_BY` - Item-based access control
- `KNOWS` - NPC relationship network

### Common Cypher Patterns

#### 1. Query Current Location

```cypher
MATCH (p:Player {id: 'player'})-[:IST_IN]->(location:Location)
RETURN location.id, location.name, location.description
```

#### 2. List Items in Location

```cypher
MATCH (p:Player {id: 'player'})-[:IST_IN]->(loc:Location)
MATCH (item:Item)-[:IST_IN]->(loc)
RETURN item.id, item.name
```

#### 3. Show Available Exits

```cypher
MATCH (p:Player {id: 'player'})-[:IST_IN]->(current:Location)
MATCH (current)-[:ERREICHT]->(target:Location)
RETURN target.id, target.name
```

#### 4. Move Player Between Locations

```cypher
MATCH (p:Player {id: 'player'})-[old:IST_IN]->(current:Location)
MATCH (current)-[:ERREICHT]->(target:Location {id: $to_location})
DELETE old
CREATE (p)-[:IST_IN]->(target)
RETURN target.id, target.name, target.description
```

#### 5. Pickup Item

```cypher
MATCH (p:Player {id: 'player'})-[:IST_IN]->(loc:Location)
MATCH (i:Item {id: $item})-[old:IST_IN]->(loc)
DELETE old
CREATE (p)-[:TRÄGT]->(i)
RETURN i.name, loc.name
```

#### 6. Drop Item

```cypher
MATCH (p:Player {id: 'player'})-[:IST_IN]->(loc:Location)
MATCH (p)-[old:TRÄGT]->(i:Item {id: $item})
DELETE old
CREATE (i)-[:IST_IN]->(loc)
RETURN i.name, loc.name
```

### Query Best Practices

1. **Always use parameterized queries:** `{id: $item_id}` instead of string concatenation
2. **Match before operations:** Verify entities exist before DELETE/CREATE
3. **Return meaningful data:** Include names and descriptions for user feedback
4. **Single responsibility:** One query per operation
5. **Avoid optional matches:** Assume valid data structure

### Database Constraints

**Created by `01-neo4j_dbsetup.ipynb`:**

```cypher
// Unique IDs
CREATE CONSTRAINT FOR (p:Player) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT FOR (l:Location) REQUIRE l.id IS UNIQUE;
CREATE CONSTRAINT FOR (i:Item) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT FOR (n:NPC) REQUIRE n.id IS UNIQUE;

// Performance indexes
CREATE INDEX FOR (l:Location) ON (l.name);
CREATE INDEX FOR (i:Item) ON (i.name);
```

### Accessing Query Results

**Neo4j Driver Returns:**
```python
result = session.run(query, parameters)
records = list(result)  # List of Record objects
```

**Convert to Dict:**
```python
def _run_query(self, query, params=None):
    """Execute query and return results as list of dicts"""
    with self.driver.session() as session:
        result = session.run(query, params or {})
        return [dict(record) for record in result]
```

**Important:** Dictionary keys match Cypher RETURN aliases:
- `RETURN location.name` → `{'location.name': 'Forest'}`
- `RETURN location.name AS name` → `{'name': 'Forest'}`

---

## 🔧 Common Development Tasks

### Adding a New Command

**1. Update Parser (if needed):**
```python
# src/utils/command_parser.py
# Usually no changes needed - parser is generic
```

**2. Add Model Method:**
```python
# src/model/game_model.py
def new_operation(self, param):
    query = """
        MATCH (p:Player {id: 'player'})-[:IST_IN]->(loc:Location)
        // Your Cypher query here
        RETURN result
    """
    return self._run_query(query, {'param': param})
```

**3. Add Controller Route:**
```python
# src/controller/game_controller.py
def process_command(self, parsed_command):
    action = parsed_command['action']
    targets = parsed_command['targets']

    if action == 'newcommand':
        if not targets:
            self.view.show_message('Error message')
            return
        result = self.model.new_operation(targets[0])
        if result:
            self.view.show_message(f"Success: {result}")
        else:
            self.view.show_message("Failed")
```

**4. Add View Display (if needed):**
```python
# src/view/game_view.py
def show_new_thing(self, data):
    self.console.print(f"[bold]New Thing:[/bold] {data}")
```

### Adding a New Node Type

**1. Define Schema in Notebook:**
```cypher
// In 01-neo4j_dbsetup.ipynb
CREATE CONSTRAINT FOR (n:NewType) REQUIRE n.id IS UNIQUE;
CREATE INDEX FOR (n:NewType) ON (n.name);

// Create sample nodes
CREATE (n:NewType {
    id: 'unique_id',
    name: 'Display Name',
    property: 'value'
})
```

**2. Add Model Methods:**
```python
def get_newtype(self, newtype_id):
    query = """
        MATCH (n:NewType {id: $id})
        RETURN n.id, n.name, n.property
    """
    return self._run_query(query, {'id': newtype_id})
```

**3. Update Controller Logic:**
```python
# Add command routing for new type interactions
```

### Adding a New Relationship

**1. Define in Database:**
```cypher
// Example: Connect items to NPCs
MATCH (npc:NPC {id: 'guard'})
MATCH (item:Item {id: 'key'})
CREATE (npc)-[:OWNS]->(item)
```

**2. Query the Relationship:**
```python
def get_npc_items(self, npc_id):
    query = """
        MATCH (npc:NPC {id: $npc_id})-[:OWNS]->(item:Item)
        RETURN item.id, item.name
    """
    return self._run_query(query, {'npc_id': npc_id})
```

### Debugging Neo4j Queries

**1. Test in Neo4j Browser (http://localhost:7474):**
```cypher
// Test query structure
MATCH (p:Player {id: 'player'})-[:IST_IN]->(loc:Location)
RETURN loc

// Check data existence
MATCH (n) RETURN labels(n), count(n)

// View relationships
MATCH (n)-[r]->() RETURN type(r), count(r)
```

**2. Add Debug Prints in Model:**
```python
def _run_query(self, query, params=None):
    print(f"Query: {query}")
    print(f"Params: {params}")
    result = self._run_query(query, params)
    print(f"Result: {result}")
    return result
```

**3. Use Jupyter Notebook:**
```python
# In notebooks/02-neo4j_commands.ipynb
from neo4j import GraphDatabase
driver = GraphDatabase.driver(uri, auth=(user, pwd))
with driver.session() as session:
    result = session.run(query, params)
    for record in result:
        print(dict(record))
```

### Resetting the Database

**Option 1: Delete All Nodes (in Neo4j Browser):**
```cypher
MATCH (n) DETACH DELETE n
```

**Option 2: Re-run Setup Notebook:**
```bash
jupyter notebook
# Open notebooks/01-neo4j_dbsetup.ipynb
# Run all cells
```

**Option 3: Restart Docker Container:**
```bash
docker stop textadventure-neo4j
docker rm textadventure-neo4j
# Re-run docker run command
```

---

## ⚠️ Known Issues & Constraints

### Critical Issues

#### 1. F-String Syntax Error (BLOCKING)

**Location:** `src/controller/game_controller.py:68`

**Issue:**
```python
# BROKEN CODE:
self.view.show_message(f"Du gehst in Richtung {result[0]['target.name']}")
                                                              ^
# Unmatched bracket - should be:
self.view.show_message(f"Du gehst in Richtung {result[0]['target.name']}")
```

**Impact:** Prevents code execution when `visit` command is used

**Fix Required:**
```python
# Correct version:
target_name = result[0].get('target.name', 'unknown')
self.view.show_message(f"Du gehst in Richtung {target_name}")
```

#### 2. Query Result Access Pattern Issue

**Problem:** Cypher RETURN creates dict keys like `'target.name'`, not nested dicts

**Current Code (INCORRECT):**
```python
result[0]['target']['name']  # Will fail - no nested dict
```

**Correct Pattern:**
```python
result[0]['target.name']  # Correct - dot notation in string key
```

### Design Constraints

#### 1. Single Player Only
- Hardcoded player ID: `'player'`
- No multi-player support planned
- All queries assume single player context

#### 2. No Error Recovery
- Neo4j connection failures crash program
- No retry logic for failed operations
- No validation of database state

#### 3. Simple Parser
- No synonym support (`gehen` != `visit`)
- No multi-word entity names (`red key` parsed as two words)
- No stopword filtering (`take the sword` includes `the`)

#### 4. No State Persistence
- Game state only in database
- No save/load game functionality
- Player must keep Neo4j running

#### 5. No Input Validation
- Invalid location IDs fail silently
- Invalid item IDs cause empty results
- No max inventory limit

### Technical Debt

1. **No Type Hints:** Makes refactoring harder
2. **No Logging:** Debugging requires print statements
3. **No Unit Tests:** Manual testing only
4. **Mixed Language:** German/English mix can confuse
5. **No Configuration Class:** Environment loading scattered
6. **Hardcoded Messages:** Should be externalized for i18n

---

## 🧪 Testing Strategy

### Current State

**No automated tests exist.** Testing is manual via:
- Jupyter notebooks for database queries
- Manual gameplay testing
- Neo4j Browser for data inspection

### Recommended Testing Approach

#### 1. Unit Tests (Parser)

```python
# tests/test_parser.py
import pytest
from src.utils.command_parser import CommandParser

def test_parse_simple_command():
    parser = CommandParser()
    result = parser.parse("show inventory")
    assert result['action'] == 'show'
    assert result['targets'] == ['inventory']

def test_parse_command_with_target():
    parser = CommandParser()
    result = parser.parse("take sword")
    assert result['action'] == 'take'
    assert result['targets'] == ['sword']
```

#### 2. Integration Tests (Model)

```python
# tests/test_model.py
import pytest
from src.model.game_model import GameModel

@pytest.fixture
def model():
    return GameModel()

def test_current_location(model):
    result = model.current_location()
    assert len(result) == 1
    assert 'location.name' in result[0]

def test_move_player(model):
    result = model.move_player('forest_path')
    assert result is not None
    assert result[0]['target.name'] == 'Forest Path'
```

#### 3. Functional Tests (Controller)

**Requires mock objects for View and Model**

```python
# tests/test_controller.py
from unittest.mock import Mock
from src.controller.game_controller import GameController

def test_process_quit_command():
    controller = GameController()
    controller.view = Mock()

    controller.process_command({'action': 'quit', 'targets': []})
    assert controller.running == False
```

#### 4. Database Tests

**Setup:**
- Use separate test database
- Create fixtures for test data
- Clean up after each test

```python
@pytest.fixture
def test_db():
    # Setup test database
    yield driver
    # Cleanup: MATCH (n) DETACH DELETE n
```

---

## 🗺️ Future Roadmap Context

### Phase 2: Core Mechanics (Current Focus)

**Next Priorities:**
- [ ] Fix f-string syntax error
- [ ] Implement proper error handling
- [ ] Add NPC dialog system
- [ ] Create quest mechanics (WANTS/GIVES relationships)
- [ ] Expand parser to handle more commands
- [ ] Write comprehensive story data

### Phase 3: LLM Integration (Upcoming)

**Planned Features:**
- Dynamic narrator using Ollama
- NPC personalities with individual prompts
- Context-aware conversations
- Emergent storytelling

**Technical Requirements:**
- Ollama local installation
- LLM service wrapper class
- Prompt template system
- Conversation history storage

### Phase 4: Intelligent Parser

**Planned Enhancements:**
- Natural language command understanding
- Embeddings-based intent recognition
- Fuzzy matching for entity names
- Multi-step command support

### Phase 5+: Advanced Features

- LangChain/LangGraph migration
- RAG for NPC knowledge
- Procedural content generation
- Multi-agent NPC interactions
- Voice-to-text input
- Multi-modal image generation

---

## 🤖 AI Assistant Guidelines

### When Working on This Project

1. **Always Read Before Modifying**
   - Read existing files before making changes
   - Understand context and patterns
   - Maintain consistency with existing code

2. **Follow Existing Patterns**
   - Use established naming conventions
   - Match current code style
   - Respect MVC boundaries

3. **Test Changes Thoroughly**
   - Verify syntax before committing
   - Test Neo4j queries in Browser first
   - Consider edge cases and empty states

4. **Document Significant Changes**
   - Update this CLAUDE.md file
   - Add comments for complex logic
   - Update README.md if setup changes

5. **Respect Language Conventions**
   - Code in English
   - UI messages in German
   - Ask if unsure about placement

6. **Avoid Over-Engineering**
   - Keep solutions simple
   - Don't add features not requested
   - Match complexity to current phase

7. **Error Handling First**
   - Add validation before operations
   - Check for None/empty results
   - Provide helpful error messages

8. **Git Best Practices**
   - Write descriptive commit messages
   - Use provided branch naming convention
   - Push only when requested

### Common Pitfalls to Avoid

❌ **Don't:**
- Add type hints unless requested (not current style)
- Create new abstractions for one-time use
- Use English in UI messages
- Skip testing Cypher queries before using them
- Assume nested dict structure in query results
- Push to main/master without permission

✅ **Do:**
- Test queries in Neo4j Browser first
- Validate inputs early in controller
- Return helpful error messages
- Use existing view methods for output
- Ask for clarification when unclear
- Update CLAUDE.md when patterns change

---

## 📚 Key Resources

### Documentation Files

- **Architecture:** `docs/architecture_idea.md`
- **Cypher Reference:** `docs/neo4j_cheatsheet.md`
- **Neo4j Setup:** `docs/neo4j_docker.md`
- **Project Setup:** `README.md`

### Development Tools

- **Neo4j Browser:** http://localhost:7474 (when Docker running)
- **Jupyter Notebooks:** `notebooks/` directory
- **Rich Documentation:** https://rich.readthedocs.io/

### Learning Resources

- **Neo4j Cypher Manual:** https://neo4j.com/docs/cypher-manual/
- **Rich Library:** https://github.com/Textualize/rich
- **Python MVC Pattern:** Various online tutorials

---

## 📝 Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-08 | 1.0 | Initial CLAUDE.md creation |

---

## 🤝 Contributing

This is a learning project. When contributing:

1. Understand the current phase and roadmap
2. Follow established patterns and conventions
3. Test thoroughly before committing
4. Update documentation as needed
5. Ask questions when uncertain

**Remember:** The goal is learning and clean architecture, not just features.

---

**End of CLAUDE.md**
