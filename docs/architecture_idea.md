# RagVenture - Architektur-Übersicht

Dieses Dokument beschreibt die Idee der Architektur des Text-Adventure-Spiels. Gilt zur Orientierung, nicht als Vorlage.

---

## Komponenten-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                         SPIELER                             │
│                  (tippt Befehle ein)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     GAME CONTROLLER                         │
│  • Nimmt User Input entgegen                                │
│  • Koordiniert alle Komponenten                             │
│  • Game Loop                                                │
└──────┬──────────────────────────────┬───────────────────────┘
       │                              │
       ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│     PARSER       │          │    GAME MODEL    │
│                  │          │                  │
│ "go north"       │          │  Neo4j Database  │
│      ↓           │          │                  │
│ ParsedCommand    │          │ • Player State   │
│ {                │          │ • Locations      │
│   verb: "go"     │          │ • Items          │
│   noun: "north"  │          │ • NPCs           │
│ }                │          │ • Relationships  │
└──────────────────┘          └──────────────────┘
       │                              │
       └──────────┬───────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │   GAME VIEW    │
         │                │
         │  Rich Console  │
         │  • Output      │
         │  • Panels      │
         │  • Formatting  │
         └────────────────┘
```

---

## Die 3 Hauptkomponenten

### 1. PARSER (`src/utils/parser.py`)

**Aufgabe**: Menschliche Sprache → Strukturierte Befehle

**Beispiele:**
```python
Input:  "nimm das goldene schwert"
Output: ParsedCommand(verb="take", noun="goldene schwert")

Input:  "n"
Output: ParsedCommand(verb="go", noun="north")

Input:  "gib schwert dem wächter"
Output: ParsedCommand(verb="give", noun="schwert", target="wächter")
```

**Funktionen:**
- Tokenisierung (Text in Wörter zerlegen)
- Synonym-Auflösung ("nimm" = "take" = "hol")
- Füllwörter entfernen ("das", "dem", "der")
- Validierung (ist Befehl vollständig?)
- Error Messages generieren

---

### 2. MODEL (`src/model/game_model.py`)

**Aufgabe**: Spielwelt-Zustand in Neo4j verwalten

**Kern-Funktionen:**

```python
# Player Operations
get_player_location() → "forest_entrance"
move_player(direction) → True/False
get_player_inventory() → [Item, Item]
add_to_inventory(item_id)
remove_from_inventory(item_id)

# Location Operations
get_location_info(location_id) → Location(name, description, items, npcs)
get_available_exits(location_id) → ["north", "east"]

# Item Operations
get_item(item_id) → Item(name, description)
pickup_item(item_id, player_id)
drop_item(item_id, location_id)

# NPC Operations
get_npc(npc_id) → NPC(name, dialogue)
talk_to_npc(npc_id) → "dialogue text"
```

**Neo4j Queries:**
- `MATCH (p:Player)-[:IST_IN]->(l:Location)` - Wo ist der Spieler?
- `MATCH (l:Location)-[e:ERREICHT {direction: 'north'}]->(l2:Location)` - Wohin kann ich gehen?
- `MATCH (i:Item)-[:LIEGT_IN]->(l:Location)` - Welche Items liegen hier?
- `MATCH (p:Player)-[:TRÄGT]->(i:Item)` - Was habe ich im Inventar?

---

### 3. GAME CONTROLLER (`src/controller/game_controller.py`)

**Aufgabe**: Orchestriert alle Komponenten

**Pseudo-Code:**
```python
def process_command(raw_input):
    # 1. Parse User Input
    command = parser.parse(raw_input)

    # 2. Validate Command
    is_valid, error = parser.validate_command(command)
    if not is_valid:
        view.show_error(error)
        return

    # 3. Execute Command via Model
    if command.verb == "go":
        success = model.move_player(command.noun)
        if success:
            new_location = model.get_current_location()
            view.show_location(new_location)
        else:
            view.show_error("Du kannst dort nicht hingehen")

    elif command.verb == "take":
        success = model.pickup_item(command.noun)
        if success:
            view.show_message("Du nimmst das Item auf")
        else:
            view.show_error("Item nicht gefunden")

    elif command.verb == "inventory":
        items = model.get_player_inventory()
        view.show_inventory(items)

    # ... weitere Befehle
```

---

## Konkreter Workflow (Beispiel)

**Spieler tippt:** `"geh nach norden"`

```
1. Controller empfängt Input
   ↓
2. Parser verarbeitet:
   "geh nach norden"
   → ParsedCommand(verb="go", noun="north")
   ↓
3. Controller validiert:
   ✓ Befehl ist vollständig
   ✓ "go" braucht eine Richtung → vorhanden
   ↓
4. Controller ruft Model:
   success = model.move_player("north")
   ↓
5. Model führt Neo4j Query aus:
   - Wo ist Player? → "forest_entrance"
   - Gibt es Exit "north"?
     MATCH (current:Location {id: 'forest_entrance'})
           -[e:ERREICHT {direction: 'north'}]->
           (target:Location)
   - Ja → "dark_cave" gefunden
   - UPDATE Player Relationship
   ↓
6. Model gibt zurück:
   success = True
   ↓
7. Controller holt neue Location Details:
   location = model.get_location_info("dark_cave")
   → Location(
       name="Dunkle Höhle",
       description="Es ist kalt und dunkel...",
       exits=["south", "east"]
     )
   ↓
8. Controller gibt an View:
   view.show_location(location)
   ↓
9. Rich Console zeigt:
   ┌─ Dunkle Höhle ────────────┐
   │ Es ist kalt und dunkel... │
   │                            │
   │ Ausgänge: süd, ost        │
   └───────────────────────────┘
```

---

## Build-Reihenfolge

### Phase 1: Parser (isoliert testbar)
- **Input**: String
- **Output**: ParsedCommand
- **Dependencies**: Keine
- **Testbar**: Ja, ohne DB

### Phase 2: Model (braucht Neo4j)
- **Input**: Method Calls
- **Output**: Game State
- **Dependencies**: Neo4j Connection
- **Testbar**: Ja, mit Test-DB

### Phase 3: Controller erweitern
- **Input**: User Input
- **Output**: View Calls
- **Dependencies**: Parser + Model + View
- **Aufgabe**: Command Dispatcher implementieren

### Phase 4: View erweitern
- **Input**: Structured Data
- **Output**: Rich Console Output
- **Methoden**:
  - `show_location(location)`
  - `show_inventory(items)`
  - `show_error(message)`
  - `show_npc_dialogue(npc, text)`

---

## Datenfluss-Diagramm

```
User Input
    ↓
[Parser] → ParsedCommand
    ↓
[Controller] → validates & routes
    ↓
[Model] ← → [Neo4j Database]
    ↓
[Controller] ← returns data
    ↓
[View] → Rich Console Output
    ↓
User sees result
```

---

## Design Patterns

- **MVC Pattern**: Model-View-Controller Separation
- **Command Pattern**: Jeder Befehl ist strukturiert
- **Repository Pattern**: Model abstrahiert DB-Zugriffe
- **Facade Pattern**: Controller vereinfacht Interaktionen

---

**Status**: Living Document
**Letzte Aktualisierung**: November 2025
**Version**: MVP Phase 1
