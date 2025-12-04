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

### MVC Pattern (UPDATED - Smart Parser Architecture)

**Important:** Die Architektur wurde erweitert für den Smart Parser. Siehe `docs/smart_parser_architecture.md` für Details.

- **Parser** (`src/utils/command_parser.py` → zukünftig `SmartParser`):
  - ✅ NLP mit SpaCy (Verb-Extraktion, Objekt-Extraktion)
  - ✅ Command-Mapping via Sentence Transformers (Embeddings)
  - ✅ Synonym-Handling ("nimm", "hol", "greif" → `'take'`)
  - ❌ **KEIN DB-Zugriff** (MVC-Prinzip!)
  - Output: `{'command': str, 'object_text': str, 'adjectives': list, 'confidence': float, 'raw': str}`

- **Controller** (`src/controller/game_controller.py`):
  - ✅ Parser → Model → View koordinieren
  - ✅ **Entity-Matching** (Text → DB-ID via Similarity-Berechnung mit gecachten Entities)
  - ✅ Entscheidungen treffen (Confidence-Thresholds, Nachfrage-Dialoge)
  - ✅ Ablaufsteuerung
  - ❌ **KEINE Business-Logik** (gehört ins Model)

- **Model** (`src/model/game_model.py`):
  - ✅ Neo4j database operations
  - ✅ **Gibt komplette Listen zurück** (nicht einzelne Matches!)
  - ✅ Business-Validierung (ist Item nehmbar? ist Location erreichbar?)
  - ✅ Aktionen ausführen (take_item, drop_item, move_player)
  - ❌ **KEIN Entity-Matching** (wandert in Controller)

- **View** (`src/view/game_view.py`):
  - ✅ Rich terminal UI, display logic only
  - (Zukünftig: Dialog-Anzeige für Ja/Nein, Multiple Choice)

**Merksatz:**
> **Parser versteht Sprache. Controller orchestriert. Model verwaltet Daten und Regeln.**

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

**Command Processing Flow (NEUE ARCHITEKTUR):**
```
User Input
    ↓
Parser (NLP + Command-Mapping, KEIN DB!)
    ↓ {'command': 'take', 'object_text': 'Schlüssel', 'adjectives': ['goldenen'], ...}
Controller (Entity-Matching mit gecachten Items)
    ↓ Similarity-Berechnung → {'item_id': 'schluessel', 'similarity': 0.89}
Controller (Entscheidung: Confidence OK?)
    ↓
Model (Aktion ausführen: take_item('schluessel'))
    ↓
Controller
    ↓
View → Terminal
```

**Parser Output Format (SMART PARSER - NEUES FORMAT):**
```python
{
    'command': str,          # 'take', 'drop', 'visit', 'examine', 'read', 'use', 'show', 'quit'
    'confidence': float,     # 0.0 - 1.0 (Verb-Matching Confidence)
    'object_text': str,      # Objekt-Name aus NLP (z.B. "Schlüssel", "Taverne")
    'adjectives': list,      # Liste von Adjektiven (z.B. ["goldenen", "alten"])
    'raw': str,              # Original-Input für Logging/Debugging
    'verb_lemma': str        # Erkanntes Verb-Lemma (z.B. "nehmen") - für Debugging
}
```

**Alte Parser Output Format (Einfacher Parser - noch aktiv):**
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

**Adding a new Model method (gibt KOMPLETTE LISTE zurück):**
```python
def get_items_at_location(self, location_id=None):
    """
    Gibt ALLE Items an der Location zurück (mit Embeddings!)
    Model macht KEIN Matching - nur Daten liefern
    """
    query = """
    MATCH (p:Player {id: 'player'})-[:IST_IN]->(loc:Location)
    MATCH (i:Item)-[:IST_IN]->(loc)
    RETURN i.id as id, i.name as name,
           i.description as description,
           i.name_embedding as embedding
    """
    return self._run_query(query)
```

**Adding a new Controller command (NEUE ARCHITEKTUR):**
```python
elif parsed['command'] == 'take':
    # 1. Controller prüft Parser-Confidence
    if parsed['confidence'] < 0.5:
        self.view.show_message("Ich habe dich nicht verstanden.")
        return

    # 2. Controller holt Items (gecacht oder vom Model)
    items = self.current_location_cache['items']
    # oder: items = self.model.get_items_at_location()

    # 3. Controller macht Entity-Matching (Similarity-Berechnung)
    match = self._find_best_match(
        parsed['object_text'],
        parsed['adjectives'],
        candidates=items
    )

    # 4. Controller entscheidet basierend auf Confidence
    if match is None:
        self.view.show_message(f"Ich sehe hier kein {parsed['object_text']}.")
        return

    if match['similarity'] < 0.5:
        # Zu unsicher → Nachfragen
        self.view.show_message(f"Meinst du {match['name']}?")
        # TODO: Dialog-System
        return

    # 5. Aktion ausführen via Model
    result = self.model.take_item(match['item_id'])
    if result:
        self.view.show_message(f"Du nimmst {result['name']}.")
```

**Controller: Entity-Matching-Methode:**
```python
def _find_best_match(self, object_text, adjectives, candidates):
    """
    Findet bestes Match via Similarity (im Controller, nicht im Model!)

    Args:
        object_text: "Schlüssel" (vom Parser)
        adjectives: ["goldenen"] (vom Parser)
        candidates: Liste von Items/Locations (gecacht oder vom Model)

    Returns:
        {'item_id': 'schluessel', 'name': '...', 'similarity': 0.89} oder None
    """
    search_text = ' '.join(adjectives + [object_text])
    search_embedding = self.sentence_model.encode(search_text)

    best_match = None
    best_similarity = 0.0

    for item in candidates:
        similarity = util.cos_sim(search_embedding, item['embedding'])[0][0].item()
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = {
                'item_id': item['id'],
                'name': item['name'],
                'similarity': similarity
            }

    return best_match if best_similarity > 0.3 else None
```

### Known Gotchas

1. **Smart Parser Output** - Neues Format! `object_text` ist String, `adjectives` ist Liste. Alte Parser: `targets[0]`
2. **Entity-Matching gehört in Controller** - Model liefert KOMPLETTE Listen, Controller matched
3. **Parser hat KEINEN DB-Zugriff** - MVC-Prinzip: Parser = NLP, Model = Daten
4. **Python dict vs set syntax** - `{'key': value}` not `{'key', value}`
5. **Relationship directions matter** - `(a)-[:REL]->(b)` is different from `(a)<-[:REL]-(b)`
6. **Cache issues** - Restart `python src/main.py` after code changes (Python caches modules)
7. **Label filtering** - Use `:Item` in MATCH or `WHERE 'Item' IN labels(entity)` to filter node types
8. **Embeddings in DB** - Items/Locations haben `name_embedding` Property (bereits vorhanden!)

## Documentation

- `docs/smart_parser_architecture.md` - **Smart Parser Architektur (MVC-konform, Parser ohne DB-Zugriff)**
- `docs/architecture_notes_dialog_caching.md` - **Konzepte: Dialog-System & Caching-Strategie**
- `docs/architecture_idea.md` - MVC-Architektur mit aktuellen Verantwortlichkeiten
- `docs/neo4j_cheatsheet.md` - Comprehensive Cypher WHERE clause reference
- `docs/neo4j_docker.md` - Docker setup details
- `README.md` - Setup instructions and roadmap
- `notebooks/01-neo4j_dbsetup.ipynb` - Database initialization (run this first!)
- `notebooks/02-neo4j_commands.ipynb` - Query testing and experimentation
- `notebooks/03-smart-parser.ipynb` - **Smart Parser Experimente und Tests (77% Accuracy)**

## Future Roadmap Context

The codebase is designed to eventually support:
- **Smart Parser Integration** (Phase 1.5 - IN ARBEIT)
  - Parser-Klasse mit SpaCy + Sentence Transformers implementieren
  - Controller umbauen (Entity-Matching, Caching)
  - Model vereinfachen (komplette Listen statt Matching)
- **Dialog-System** (Phase 1.5+)
  - Ja/Nein-Bestätigungen bei niedrigem Confidence
  - Multiple-Choice bei mehreren ähnlichen Items
  - State-Management im Controller
- **LLM-based narrator** (Phase 3 - Ollama integration)
- **NPC personalities** with individual prompts
- **Command Pattern refactoring** (currently flat if/elif in Controller)

When making changes, keep extensibility in mind but don't over-engineer for future phases.

---

**Letzte Aktualisierung:** 4. Dezember 2024
**Aktueller Branch:** `smart-parser`
**Status:** Phase 1.5 - Smart Parser Development (Architektur definiert, Implementierung steht an)
