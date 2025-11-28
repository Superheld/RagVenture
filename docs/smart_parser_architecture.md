# Smart Parser Architektur

## Übersicht

Der Smart Parser ersetzt den einfachen `CommandParser` durch ein mehrschichtiges NLP-System, das natürliche deutsche Sätze versteht und in Game-Commands übersetzt.

**Ziel:** Von "Nimm den goldenen Schlüssel" zu `{'action': 'take', 'targets': ['schluessel'], 'raw': '...'}`

---

## 4-Schichten-Architektur

```
User Input (natürlicher deutscher Satz)
         ↓
┌────────────────────────────────┐
│  Layer 1: NLP Parsing          │  SpaCy
│  Syntax-Analyse                │
└────────────────────────────────┘
         ↓ Verb + Objekte (Namen)
┌────────────────────────────────┐
│  Layer 2: Intent Mapping       │  Sentence Transformers
│  Verb → Command                │
└────────────────────────────────┘
         ↓ Command + Objekt-Namen
┌────────────────────────────────┐
│  Layer 3: Entity Resolution    │  Neo4j DB Queries
│  Namen → IDs                   │
└────────────────────────────────┘
         ↓ Command + IDs
┌────────────────────────────────┐
│  Layer 4: Output Formatting    │
│  Controller-kompatibles Dict   │
└────────────────────────────────┘
         ↓
Controller (unverändert)
```

---

## Layer 1: NLP Parsing (SpaCy)

**Technologie:** SpaCy mit `de_dep_news_trf` (Transformer-Modell für deutsches Dependency Parsing)

**Input:** Roher Text-String
**Output:** Strukturierte linguistische Information

**Aufgaben:**
1. **Verb-Extraktion:** Finde das Hauptverb (ROOT im Dependency-Tree)
2. **Objekt-Extraktion:** Finde alle relevanten Objekte (Dependency-Labels: `oa`, `obj`, `dobj`, `pobj`)
3. **Nominalphrasen-Rekonstruktion:** Kombiniere Adjektive + Nomen ("goldenen Schlüssel")
4. **Trennbare Verben:** Erkenne Verb-Präfixe (`svp`: "nimm...auf" → "aufnehmen")

**Beispiel:**
- Input: `"Nimm den goldenen Schlüssel auf"`
- Output: `{verb: "aufnehmen", objects: ["goldenen Schlüssel"]}`

**Relevante SpaCy-Konzepte:**
- `token.dep_` - Dependency-Relation (ROOT, oa, svp, ...)
- `token.lemma_` - Grundform des Verbs (nehmen statt nimm)
- `token.children` - Abhängige Tokens (Adjektive zu Nomen)
- Deutsche Dependency-Labels: `oa` (Akkusativobjekt), `nk` (Nomenkomplex), `svp` (separable verb prefix)

---

## Layer 2: Intent Mapping (Sentence Transformers)

**Technologie:** Sentence Transformers mit `paraphrase-multilingual-MiniLM-L12-v2`

**Input:** Verb (Lemma) aus Layer 1
**Output:** Game-Command (`take`, `drop`, `visit`, `show`, `quit`)

**Ansätze:**

### Variante A: Verb-Embedding-Matching
- Embeddings für bekannte Verben pro Command vorberechnen
- User-Verb einbetten und Cosine-Similarity berechnen
- Höchste Similarity = gewählter Command

```
Commands:
- take: ['nehmen', 'holen', 'packen', 'greifen', 'schnappen']
- drop: ['ablegen', 'werfen', 'lassen']
- visit: ['gehen', 'laufen', 'besuchen', 'bewegen']
- show: ['zeigen', 'schauen', 'auflisten']
```

### Variante B: Ganzer-Satz-Matching
- Template-Sätze pro Command
- Ganzen Input-Satz einbetten
- Bester Match = Command
- Vorteil: Funktioniert auch bei Umgangssprache ohne klares Verb

**Fallback:** Bei niedriger Confidence (<0.6) → Nachfrage an User oder Fehler

**Beispiel:**
- Input: `"schnappen"` (Lemma)
- Similarity zu "nehmen": 0.78
- Output: `"take"` (confidence: 0.78)

---

## Layer 3: Entity Resolution (Neo4j DB)

**Technologie:** Cypher-Queries gegen Neo4j-Graph

**Input:** Objekt-Namen aus Layer 1 (z.B. "goldenen Schlüssel", "Taverne")
**Output:** Entity-IDs aus DB (z.B. "schluessel", "taverne")

**Strategien:**

### Strategie 1: Exaktes String-Matching
- Case-insensitive Vergleich mit `Item.name` und `Location.name`
- Einfach, schnell, deterministisch
- Problem: Keine Fehlertoleranz

### Strategie 2: Full-Text Index (Fuzzy)
- Neo4j Full-Text Search mit `~` (Tilde) für Fuzzy-Matching
- Toleriert Tippfehler und Teilwort-Matches
- Erfordert Index-Erstellung

### Strategie 3: Embedding-basiert (Semantisch)
- Items/Locations haben `name_embedding`-Property
- Vector-Similarity-Search
- Erkennt Synonyme ("Schwert" matched "Klinge")
- Problem: Vector-Indexes nur auf Nodes, nicht auf Properties (Neo4j 5.x)

**Kontext-Awareness:**
- Bei `take`/`drop`: Nur Items an aktueller Location bzw. in Inventory durchsuchen
- Bei `visit`: Nur verbundene Locations (via `ERREICHT`) durchsuchen
- Reduziert Ambiguität

**Beispiel:**
- Input: `"goldenen Schlüssel"`
- Query: `MATCH (i:Item) WHERE toLower(i.name) CONTAINS 'schlüssel' RETURN i.id`
- Output: `"schluessel"`

---

## Layer 4: Output Formatting

**Input:** Command + Entity-IDs
**Output:** Controller-kompatibles Dictionary

**Format (kompatibel mit bestehendem Controller):**
```python
{
    'action': str,      # 'take', 'drop', 'visit', 'show', 'quit'
    'targets': list,    # ['schluessel'] oder [] wenn keine
    'raw': str         # Original-Input für Logging/Debugging
}
```

**Zusätzliche Metadaten (optional):**
```python
{
    'confidence': float,      # Confidence-Score aus Layer 2
    'resolved_entities': [],  # Mapping Name → ID für Debugging
}
```

---

## Implementierung: SmartParser-Klasse

**Schnittstelle:**
```python
class SmartParser:
    def __init__(self, game_model):
        """
        game_model: GameModel-Instanz für DB-Zugriff (Layer 3)
        """

    def parse(self, input_text):
        """
        Hauptmethode - gibt Controller-kompatibles Dict zurück

        Returns:
            dict: {'action': str, 'targets': list, 'raw': str}
        """
```

**Interne Methoden:**
```python
_extract_syntax(text)          # Layer 1: SpaCy
_verb_to_command(verb_lemma)   # Layer 2: Sentence Transformers
_resolve_entity(name, context) # Layer 3: DB-Lookup
```

**Dependency Injection:**
- `GameModel` wird im Constructor übergeben (für DB-Zugriff)
- SpaCy- und Sentence-Transformer-Modelle werden beim Init geladen (lazy loading möglich)

---

## Integration in bestehende Architektur

**Controller-Änderung (minimal):**
```python
# Alt:
self.parser = CommandParser()

# Neu:
self.parser = SmartParser(self.model)

# parse()-Aufruf bleibt gleich!
parsed = self.parser.parse(command)
```

**Keine Änderungen nötig in:**
- GameModel (DB-Logik)
- GameView (UI)
- Controller-Command-Handling (process_command)

**Backwards-Compatibility:**
- Alte Commands ("take schluessel") funktionieren weiterhin
- Neue natürliche Sätze ("nimm den goldenen Schlüssel") funktionieren auch

---

## Performance-Überlegungen

**Model Loading:**
- SpaCy TRF-Modell: ~500MB, Ladezeit ~2-5s
- Sentence Transformer: ~120MB, Ladezeit ~1s
- **Lösung:** Models beim Start laden (einmalig), dann im RAM halten

**Inference-Zeit:**
- SpaCy: ~50-100ms pro Satz
- Sentence Transformer: ~10-30ms pro Embedding
- DB-Query: ~5-20ms
- **Gesamt:** ~100-200ms pro User-Input → Akzeptabel für Text-Adventure

**Optimierungen:**
- Command-Embeddings vorberechnen (Cache)
- Entity-Embeddings vorberechnen (falls Strategie 3)
- Batch-Processing bei mehreren Commands (aktuell nicht nötig)

---

## Offene Architektur-Fragen

### 1. Wo werden Command-Verb-Mappings gespeichert?
- **Option A:** Python-Dict im SmartParser (flexibel, Code-nah)
- **Option B:** Neo4j Command-Nodes mit Verb-Properties (data-driven, editierbar ohne Code)
- **Option C:** JSON-Config-File (Mittelweg)

### 2. Welche Entity-Resolution-Strategie?
- Start: Strategie 1 (Exakt) - einfach
- Erweitern: Strategie 2 (Fuzzy) - fehlertoleranter
- Future: Strategie 3 (Embeddings) - semantisch

### 3. Embedding-Storage in DB?
- Relationships mit Embeddings für Verb-Action-Mapping?
- Items/Locations mit name_embeddings?
- **Problem:** Vector-Indexes nur auf Nodes (Neo4j-Limitation)

### 4. Multi-Command-Sätze?
"Nimm den Schlüssel und geh zur Taverne"
- Aktuell: Nicht unterstützt (nur 1 ROOT-Verb)
- Erkennung: SpaCy findet koordinierte Verben (`cj`-Dependency)
- Handling: Zwei separate Commands generieren?

---

## Roadmap

**Phase 1 (MVP):**
- [x] SpaCy Syntax-Parsing testen (Notebook)
- [ ] Sentence Transformer Verb-Matching implementieren
- [ ] Entity-Resolution (Strategie 1: Exakt)
- [ ] SmartParser-Klasse implementieren
- [ ] Controller-Integration

**Phase 2 (Robustheit):**
- [ ] Fuzzy Entity-Resolution (Full-Text)
- [ ] Confidence-Thresholds und Fehlerbehandlung
- [ ] Trennbare Verben vollständig unterstützen

**Phase 3 (Advanced):**
- [ ] Embedding-basierte Entity-Resolution
- [ ] Multi-Command-Parsing
- [ ] Context-Aware Disambiguation ("es" = letztes Objekt)
- [ ] Verb-Mappings in DB auslagern

---

## Verwandte Dokumente

- `architecture_idea.md` - Ursprüngliche Vision (MVC, LLM-Integration)
- `neo4j_cheatsheet.md` - Cypher-Query-Referenz
- `CLAUDE.md` - Aktueller Parser-Output-Format
- `notebooks/03-smart-parser.ipynb` - Experimente und Tests
