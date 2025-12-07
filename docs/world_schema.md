# World Schema - RagVenture

Definiert die Struktur der Spielwelt in Neo4j.

---

## Relationship-Types (Schema)

Alle erlaubten Relationships im Graph:

| Relationship | Von | Nach | Bidirektional | Bedeutung |
|--------------|-----|------|---------------|-----------|
| `IST_IN` | Item, NPC, Player | Location | Nein | Containment/Platzierung |
| `TRÄGT` | Player, NPC | Item | Nein | Inventar |
| `ERREICHT` | Location | Location | **Ja** | Verbindung zwischen Orten |
| `ÖFFNET` | Item | Item, Location | Nein | Schlüssel öffnet Truhe/Tür |
| `KANN_ANZÜNDEN` | Item | Item | Nein | Tool zündet Objekt an |
| `BELEUCHTET` | Item | Location | Nein | Lichtquelle beleuchtet Ort |
| `KANN_BRECHEN` | Item | Item | Nein | Tool zerstört Objekt |

**Wichtig:** Nur diese Relationship-Types verwenden! Das Notebook zeigt Warnings bei unbekannten Types.

---

## Node-Types

### Location

**Label:** `:Location`

**Required Properties:**
```python
{
    'id': str,           # Unique identifier (lowercase, no spaces)
    'name': str,         # Display name
    'description': str   # Text description
}
```

**Optional Properties:**
```python
{
    'is_dark': bool,          # Default: False
    'requires_light': bool,   # Default: False (Braucht Lichtquelle zum Betreten)
    'is_locked': bool         # Default: False
}
```

**Auto-Generated:**
```python
{
    'name_emb': List[float],        # Vector (384 dim)
    'description_emb': List[float]  # Vector (384 dim)
}
```

**Beispiel:**
```python
create_location(
    'finsterwald',
    'Finsterwald',
    'Ein dunkler, übelriechender Wald...',
    is_dark=True,
    requires_light=True
)
```

---

### Item

**Label:** `:Item`

**Required Properties:**
```python
{
    'id': str,
    'name': str,
    'description': str
}
```

**Optional Properties:**
```python
{
    'is_takeable': bool,       # Default: True
    'is_usable': bool,         # Default: False
    'is_readable': bool,       # Default: False
    'is_container': bool,      # Default: False
    'is_locked': bool,         # Default: None (nur bei Containern)
    'is_lit': bool,            # Default: None (nur bei Lichtquellen)
    'is_light_source': bool,   # Default: False
    'item_type': str,          # Default: None (z.B. 'key', 'weapon', 'tool')
    'weight': float            # Default: None
}
```

**Auto-Generated:**
```python
{
    'name_emb': List[float],
    'description_emb': List[float],
    'synonyms_emb': List[float]  # Nur wenn synonyms übergeben
}
```

**Beispiel:**
```python
create_item(
    'fackel',
    'Flackernde Fackel',
    'Eine alte Fackel...',
    synonyms=['Fackel', 'Lichtquelle', 'Flamme'],
    is_lit=False,
    is_light_source=True,
    is_usable=True
)
```

---

### NPC

**Label:** `:NPC`

**Required Properties:**
```python
{
    'id': str,
    'name': str,
    'description': str
}
```

**Optional Properties:**
```python
{
    'dialogue': str,           # Default: None (statischer Dialog-Text)
    'is_trader': bool,         # Default: False
    'is_quest_giver': bool     # Default: False
}
```

**Auto-Generated:**
```python
{
    'name_emb': List[float],
    'description_emb': List[float]
}
```

**Beispiel:**
```python
create_npc(
    'wirt',
    'Schenk',
    'Ein alter, grummiger Wirt...',
    dialogue='Willkommen in meiner Taverne!',
    is_trader=True
)
```

---

### Player

**Label:** `:Player`

**Required Properties:**
```python
{
    'id': 'player',  # Immer 'player'!
    'name': str,
    'description': str
}
```

**Beispiel:**
```python
create_player('player', 'Player', 'Hier könnte dein Name stehen!')
```

---

## Helper-Funktionen (Notebook)

### Node-Erstellung

```python
create_item(id, name, description, synonyms=None, **kwargs)
create_location(id, name, description, **kwargs)
create_npc(id, name, description, **kwargs)
create_player(id='player', name='Player', description='...')
```

### Relationship-Erstellung

**Generisch:**
```python
create_relationship(from_id, rel_type, to_id)
```

**Semantisch (empfohlen):**
```python
connect_locations(loc1_id, loc2_id)          # Bidirektional ERREICHT
place_item(item_id, location_id)             # IST_IN
place_npc(npc_id, location_id)               # IST_IN
place_player(player_id, location_id)         # IST_IN
give_item_to_npc(item_id, npc_id)            # TRÄGT
make_key_unlock(key_id, target_id)           # ÖFFNET
make_tool_light(tool_id, target_id)          # KANN_ANZÜNDEN
make_tool_break(tool_id, target_id)          # KANN_BRECHEN
make_light_illuminate(light_id, location_id) # BELEUCHTET
```

---

## Beispiel-Welt

**Aktuelle Spielwelt:**

```
Locations (4):
  - taverne (Mo's Taverne)
  - marktplatz (Hub)
  - finsterwald (dunkel, braucht Licht)
  - schmiede

Items (8):
  - truhe (verschlossen, Container)
  - schluessel (öffnet Truhe)
  - fackel (Lichtquelle, noch nicht angezündet)
  - streichhoelzer (zündet Fackel an)
  - hammer (kann Truhe zerbrechen)
  - beutel (Container)
  - schwert (Waffe)
  - buch (lesbar)

NPCs (2):
  - wirt (in Taverne, trägt Streichhölzer)
  - haendler (auf Marktplatz)

Player (1):
  - player (startet auf Marktplatz)
```

**Quest-Chains:**

1. **Truhe öffnen:**
   - Weg A: Schlüssel finden → Truhe öffnen
   - Weg B: Hammer holen → Truhe zerbrechen

2. **Finsterwald betreten:**
   - Fackel holen
   - Streichhölzer vom Wirt bekommen (handeln?)
   - Fackel anzünden
   - Finsterwald betreten (beleuchtet)

---

## Constraints & Indexes

**Unique Constraints:**
```cypher
CREATE CONSTRAINT location_id FOR (l:Location) REQUIRE l.id IS UNIQUE
CREATE CONSTRAINT item_id FOR (i:Item) REQUIRE i.id IS UNIQUE
CREATE CONSTRAINT npc_id FOR (n:NPC) REQUIRE n.id IS UNIQUE
CREATE CONSTRAINT player_id FOR (p:Player) REQUIRE p.id IS UNIQUE
```

**Property Indexes:**
```cypher
CREATE INDEX location_name FOR (l:Location) ON (l.name)
CREATE INDEX item_name FOR (i:Item) ON (i.name)
CREATE INDEX npc_name FOR (n:NPC) ON (n.name)
```

**Vector Indexes (für Smart Parser):**
```cypher
# Location Embeddings
CREATE VECTOR INDEX location_name_index FOR (l:Location) ON l.name_emb
CREATE VECTOR INDEX location_description_index FOR (l:Location) ON l.description_emb

# Item Embeddings
CREATE VECTOR INDEX item_name_index FOR (i:Item) ON i.name_emb
CREATE VECTOR INDEX item_description_index FOR (i:Item) ON i.description_emb
CREATE VECTOR INDEX item_synonyms_index FOR (i:Item) ON i.synonyms_emb

# NPC Embeddings
CREATE VECTOR INDEX npc_name_index FOR (n:NPC) ON n.name_emb
CREATE VECTOR INDEX npc_description_index FOR (n:NPC) ON n.description_emb
```

---

## Design-Entscheidungen

### Warum Relationships statt nur Properties?

**Properties = State (veränderlich):**
- `is_locked`, `is_lit` → ändern sich im Spielverlauf

**Relationships = Schema (statisch):**
- `ÖFFNET`, `KANN_ANZÜNDEN` → definieren Möglichkeiten

**Vorteil:**
- Neue Interaktionen ohne Code-Änderung hinzufügen
- Graph visualisiert Möglichkeiten
- Discovery: "Was kann ich mit diesem Item machen?" → `MATCH (item)-[r]->() RETURN r`

### Warum Helper-Funktionen?

**Problem:** Neo4j ist schema-less → Tippfehler möglich
```cypher
(schluessel)-[:ÖFFNE]->(truhe)   # Falsch! Sollte ÖFFNET sein
```

**Lösung:** Helper-Funktionen mit Konstanten
```python
make_key_unlock('schluessel', 'truhe')  # Nutzt REL_ÖFFNET konstant
```

### Warum Embeddings für alle Properties?

Smart Parser nutzt Vector-Similarity für:
- Fuzzy-Matching ("nimm den goldnen Schlüssel" → findet "Goldener Schlüssel")
- Synonym-Erkennung ("nimm die Fackel" → findet auch "Lichtquelle")
- Beschreibungs-Matching ("nimm das schwere Ding" → findet "Hammer")

---

## Erweiterungen

### Neue Location hinzufügen

```python
# 1. Location erstellen
create_location('krypta', 'Düstere Krypta', '...', is_dark=True)

# 2. Verbinden
connect_locations('finsterwald', 'krypta')

# 3. Items platzieren
place_item('skelettschluessel', 'krypta')
```

### Neues Item mit Interaktion

```python
# Item erstellen
create_item(
    'dietrich',
    'Dietrich',
    'Ein rostiger Dietrich...',
    synonyms=['Dietrich', 'Lockpick'],
    item_type='tool',
    is_usable=True
)

# Interaktion definieren
make_key_unlock('dietrich', 'truhe')  # Kann auch Truhe öffnen
```

### Neuer Relationship-Type

1. **Konstante hinzufügen** (Notebook):
```python
REL_GIBT = "GIBT"  # NPC gibt Item bei Quest
```

2. **Helper-Funktion erstellen**:
```python
def make_npc_give_quest_reward(npc_id, item_id):
    create_relationship(npc_id, REL_GIBT, item_id)
```

3. **Nutzen**:
```python
make_npc_give_quest_reward('wirt', 'goldener_schluessel')
```

---

**Version:** 1.0
**Letzte Aktualisierung:** Dezember 2025
**Status:** Production-Ready ✅
