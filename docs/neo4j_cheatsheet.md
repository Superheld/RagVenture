# Neo4j & Cypher Cheat Sheet

Schnellreferenz für Neo4j Graph-Datenbank und Cypher Query Language.

---

## 🎯 Cypher Grundlagen

### Kommentare
```cypher
// Einzeiliger Kommentar
/* Mehrzeiliger Kommentar */
```

### CREATE - Nodes erstellen
```cypher
CREATE (n:Person {name: "Alice", age: 30})

// Mehrere Nodes + Relationship
CREATE (a:Person {name: "Alice"})-[:KNOWS {since: 2020}]->(b:Person {name: "Bob"})
```

### MERGE - Create or Match (verhindert Duplikate)
```cypher
// Nur nach ID suchen, Rest mit SET
MERGE (p:Person {id: "alice123"})
SET p.name = "Alice", p.age = 30

// Mit ON CREATE / ON MATCH
MERGE (p:Person {id: "alice123"})
ON CREATE SET p.created = timestamp(), p.name = "Alice"
ON MATCH SET p.updated = timestamp()
```

### MATCH - Daten abfragen
```cypher
// Node finden
MATCH (p:Person {name: "Alice"})
RETURN p.name, p.age

// Mit WHERE-Filter
MATCH (p:Person)
WHERE p.age > 25 AND p.name CONTAINS "Ali"
RETURN p
```

### Relationships abfragen
```cypher
// Gerichtete Beziehung
MATCH (a:Person)-[:KNOWS]->(b:Person)
RETURN a.name, b.name

// Beliebige Richtung
MATCH (a:Person)-[:KNOWS]-(b:Person)
RETURN a, b
```

### SET - Properties ändern
```cypher
MATCH (p:Person {name: "Alice"})
SET p.age = 31, p.city = "Berlin"

// Property löschen
MATCH (p:Person {name: "Alice"})
REMOVE p.age
```

### DELETE - Daten löschen
```cypher
// Node mit allen Relationships
MATCH (p:Person {name: "TestUser"})
DETACH DELETE p

// Nur Relationship
MATCH (a)-[r:KNOWS]->(b)
DELETE r

// ALLE Daten (VORSICHT!)
MATCH (n) DETACH DELETE n
```

### Aggregation & Sortierung
```cypher
// Zählen
MATCH (p:Person)
RETURN count(p)

// Sammeln
MATCH (p:Person)-[:OWNS]->(i:Item)
RETURN p.name, collect(i.name) as items

// Sortieren & Limitieren
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age DESC
LIMIT 10
```

---

## 🏗️ Schema & Constraints

### Constraints erstellen
```cypher
// Eindeutige ID
CREATE CONSTRAINT room_id IF NOT EXISTS
FOR (r:Room) REQUIRE r.id IS UNIQUE;

// Index für Performance
CREATE INDEX room_name IF NOT EXISTS
FOR (r:Room) ON (r.name);
```

### Schema anzeigen
```cypher
SHOW CONSTRAINTS
SHOW INDEXES
CALL db.schema.visualization()
```

---

## 🐍 Python Integration

### Connection Setup
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)

# Query ausführen
def run_query(query, params=None):
    with driver.session() as session:
        result = session.run(query, params or {})
        return [r.data() for r in result]

# Beispiel
rooms = run_query("MATCH (r:Room) RETURN r.name")
```

### Parametrisierte Queries
```python
# Mit Parameters (sicherer!)
query = """
MATCH (p:Player {id: $player_id})-[:LOCATED_IN]->(r:Room)
RETURN r.name
"""
result = run_query(query, {"player_id": "hero"})
```

---

## 🛠️ Debugging & Utils

### Datenbank-Überblick
```cypher
// Anzahl Nodes pro Label
MATCH (n)
RETURN labels(n) as label, count(*) as count

// Alle Relationship-Typen
MATCH ()-[r]->()
RETURN DISTINCT type(r)

// Alles löschen (VORSICHT!)
MATCH (n) DETACH DELETE n
```

### Performance
```cypher
// Query-Plan anzeigen
EXPLAIN
MATCH (r:Room {id: "start"})
RETURN r

// Mit Execution-Stats
PROFILE
MATCH (r:Room {id: "start"})
RETURN r
```

---

## 📚 Erweiterte Patterns

### OPTIONAL MATCH
```cypher
// Auch wenn keine Items vorhanden sind
MATCH (r:Room)
OPTIONAL MATCH (r)-[:CONTAINS]->(i:Item)
RETURN r.name, collect(i.name) as items
```

### WITH - Intermediate Results
```cypher
// Filtern nach Aggregat
MATCH (p:Player)-[:CARRIES]->(i:Item)
WITH p, count(i) as item_count
WHERE item_count > 5
RETURN p.name, item_count
```

### CASE - Bedingungen
```cypher
MATCH (p:Player)
RETURN p.name,
  CASE
    WHEN p.health > 80 THEN "gesund"
    WHEN p.health > 30 THEN "verletzt"
    ELSE "kritisch"
  END as status
```

---

## 🔗 Ressourcen

- **Neo4j Browser**: http://localhost:7474 (Auto-Complete mit Ctrl+Space)
- **Offizielle Docs**: https://neo4j.com/docs/cypher-cheat-sheet/5/
- **Cypher Manual**: https://neo4j.com/docs/cypher-manual/current/