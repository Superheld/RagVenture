# Smart Parser Architektur

## Übersicht

Der Smart Parser ersetzt den einfachen `CommandParser` durch ein NLP-System, das natürliche deutsche Sätze versteht und in strukturierte Parsing-Informationen übersetzt. **Wichtig:** Der Parser macht KEIN DB-Matching - das übernimmt der Controller mit Hilfe des Models (MVC-Prinzip).

**Ziel:** Von "Nimm den goldenen Schlüssel" zu `{'command': 'take', 'object_text': 'Schlüssel', 'adjectives': ['goldenen'], 'raw': '...'}`

---

## Neue 3-Schichten-Architektur (MVC-konform)

```
User Input (natürlicher deutscher Satz)
         ↓
┌────────────────────────────────┐
│  PARSER (kein DB-Zugriff!)     │
│  Layer 1: NLP Parsing (SpaCy)  │
│  Layer 2: Intent Mapping       │
└────────────────────────────────┘
         ↓ {command, object_text, adjectives, confidence}
┌────────────────────────────────┐
│  CONTROLLER (Orchestrierung)   │
│  - Empfängt Parser-Output      │
│  - Fragt Model für Matching    │
│  - Entscheidet bei Ambiguität  │
└────────────────────────────────┘
         ↓ "Finde Item: 'Schlüssel' + 'goldenen'"
┌────────────────────────────────┐
│  MODEL (DB-Logik)              │
│  - Entity-Matching mit DB      │
│  - Similarity-Berechnung       │
│  - Validierung (Item am Ort?)  │
│  - Business Logic              │
└────────────────────────────────┘
         ↓ {item_id: 'schluessel', similarity: 0.89}
┌────────────────────────────────┐
│  CONTROLLER                    │
│  - Prüft Confidence            │
│  - Führt Aktion aus            │
│  - Steuert View                │
└────────────────────────────────┘
```

---

## Architektur-Prinzipien (WICHTIG!)

### Separation of Concerns

**Parser (NLP Layer):**
- ✅ Text → Strukturierte linguistische Information
- ✅ Verb-Extraktion mit SpaCy
- ✅ Command-Matching via Embeddings
- ✅ Objekt-Namen extrahieren (mit Adjektiven)
- ❌ **KEIN DB-Zugriff**
- ❌ **KEINE Entity-Resolution**

**Controller (Orchestration Layer):**
- ✅ Parser → Model → View koordinieren
- ✅ Entscheidungen treffen (Confidence zu niedrig? → Nachfragen)
- ✅ Ablaufsteuerung (Was tun bei Fehler?)
- ✅ Model-Methoden aufrufen
- ❌ **KEINE Business-Logik** (gehört ins Model)

**Model (Data & Business Logic):**
- ✅ DB-Abfragen (Embeddings, Items, Locations)
- ✅ Entity-Matching (Text → DB-ID)
- ✅ Similarity-Berechnung
- ✅ Validierung (Item nehmbar? Am Ort vorhanden?)
- ✅ Business Rules (Spielregeln)

### Merksatz:
> **Parser versteht Sprache. Controller orchestriert. Model verwaltet Daten und Regeln.**

### Faustregel:
> Alles was mit **Daten und Logik** zu tun hat → **Model**.
> Alles was **Ablauf und UI** betrifft → **Controller**.
> Alles was **Text-Verständnis** betrifft → **Parser**.

---

## Layer 1: NLP Parsing (SpaCy) - IM PARSER

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
- Output: `{verb_lemma: "aufnehmen", objects: [{"text": "Schlüssel", "adjectives": ["goldenen"]}]}`

**Relevante SpaCy-Konzepte:**
- `token.dep_` - Dependency-Relation (ROOT, oa, svp, ...)
- `token.lemma_` - Grundform des Verbs (nehmen statt nimm)
- `token.children` - Abhängige Tokens (Adjektive zu Nomen)
- Deutsche Dependency-Labels: `oa` (Akkusativobjekt), `nk` (Nomenkomplex), `svp` (separable verb prefix)

---

## Layer 2: Intent Mapping (Sentence Transformers) - IM PARSER

**Technologie:** Sentence Transformers mit `paraphrase-multilingual-MiniLM-L12-v2`

**Input:** Verb (Lemma) aus Layer 1
**Output:** Game-Command (`take`, `drop`, `visit`, `show`, `quit`) + Confidence-Score

**Ansätze:**

### Variante A: Verb-Embedding-Matching (AKTUELL VERWENDET)
- Embeddings für bekannte Verben pro Command vorberechnen
- User-Verb einbetten und Cosine-Similarity berechnen
- Höchste Similarity = gewählter Command

```
Commands:
- take: ['nehmen', 'holen', 'packen', 'greifen', 'schnappen']
- drop: ['ablegen', 'werfen', 'lassen']
- visit: ['gehen', 'laufen', 'besuchen', 'bewegen']
- show: ['zeigen', 'schauen', 'auflisten']
- examine: ['untersuchen', 'betrachten', 'ansehen', 'prüfen']
- read: ['lesen', 'entziffern', 'durchlesen']
- use: ['benutzen', 'verwenden', 'anwenden', 'einsetzen']
```

### Variante B: Ganzer-Satz-Matching
- Template-Sätze pro Command
- Ganzen Input-Satz einbetten
- Bester Match = Command
- Vorteil: Funktioniert auch bei Umgangssprache ohne klares Verb

**Fallback:** Bei niedriger Confidence (<0.6) → Controller entscheidet (Nachfrage oder Fehler)

**Beispiel:**
- Input: `"schnappen"` (Lemma)
- Similarity zu "nehmen": 0.78
- Output: `{"command": "take", "confidence": 0.78}`

---

## Layer 3: Entity Resolution - IM MODEL (nicht im Parser!)

**Technologie:** Cypher-Queries gegen Neo4j-Graph

**Input:** Objekt-Namen aus Parser (z.B. "Schlüssel" + Adjektive: ["goldenen"])
**Output:** Entity-Match mit ID und Confidence

**Wo:** Im **GameModel** als neue Methode(n):
```python
def find_matching_item(self, item_text, adjectives=[], location_id=None):
    """
    Findet das beste passende Item basierend auf Text + Embeddings

    Args:
        item_text: Der Objekt-Name vom Parser (z.B. "Schlüssel")
        adjectives: Liste von Adjektiven (z.B. ["goldenen"])
        location_id: Optional - beschränkt Suche auf Location

    Returns:
        dict: {
            'item_id': 'schluessel',
            'name': 'Goldener Schlüssel',
            'similarity': 0.89,
            'context': 'inventory'  # oder 'location'
        }
        oder None wenn kein Match
    """
```

**Strategien:**

### Strategie 1: Exaktes String-Matching (START)
- Case-insensitive Vergleich mit `Item.name` und `Location.name`
- Teilwort-Matching: "Schlüssel" matched "Goldener Schlüssel"
- Einfach, schnell, deterministisch
- Problem: Keine Fehlertoleranz

### Strategie 2: Full-Text Index (Fuzzy)
- Neo4j Full-Text Search mit `~` (Tilde) für Fuzzy-Matching
- Toleriert Tippfehler und Teilwort-Matches
- Erfordert Index-Erstellung

### Strategie 3: Embedding-basiert (Semantisch - ZIEL)
- Items/Locations haben `name_embedding`-Property (bereits vorhanden!)
- Vector-Similarity-Search
- Erkennt Synonyme ("Schwert" matched "Klinge", "Fackel" matched "Laterne")
- Problem: Vector-Indexes nur auf Nodes, nicht auf Properties (Neo4j 5.x)

**Kontext-Awareness (WICHTIG für Validierung):**
- Bei `take`: Nur Items an aktueller Location durchsuchen
- Bei `drop`: Nur Items im Inventory durchsuchen
- Bei `visit`: Nur verbundene Locations (via `ERREICHT`) durchsuchen
- Reduziert Ambiguität und verhindert ungültige Aktionen

**Beispiel:**
- Input vom Parser: `{"object_text": "Schlüssel", "adjectives": ["goldenen"]}`
- Model kombiniert: "goldenen Schlüssel"
- Query: Hole alle Items am Ort, berechne Similarity
- Output: `{"item_id": "schluessel", "similarity": 0.89}`

---

## Parser Output Format (NEUES FORMAT!)

**Der Parser gibt KEINE IDs zurück, sondern nur Text-Informationen:**

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

**Beispiele:**

```python
# Input: "Nimm den goldenen Schlüssel"
{
    'command': 'take',
    'confidence': 0.85,
    'object_text': 'Schlüssel',
    'adjectives': ['goldenen'],
    'raw': 'Nimm den goldenen Schlüssel',
    'verb_lemma': 'nehmen'
}

# Input: "Geh zur Taverne"
{
    'command': 'visit',
    'confidence': 0.92,
    'object_text': 'Taverne',
    'adjectives': [],
    'raw': 'Geh zur Taverne',
    'verb_lemma': 'gehen'
}

# Input: "Zeig Inventar"
{
    'command': 'show',
    'confidence': 0.88,
    'object_text': 'Inventar',
    'adjectives': [],
    'raw': 'Zeig Inventar',
    'verb_lemma': 'zeigen'
}
```

---

## Controller Processing Flow (NEUER WORKFLOW)

```python
def process_command(self, user_input):
    # 1. Parser: Text → Strukturierte Info (KEIN DB-Zugriff!)
    parsed = self.parser.parse(user_input)
    # → {'command': 'take', 'object_text': 'Schlüssel', 'adjectives': ['goldenen'], ...}

    # 2. Controller: Prüfe Confidence
    if parsed['confidence'] < 0.5:
        self.view.show_message("Ich habe dich nicht verstanden.")
        return

    # 3. Controller: Routing basierend auf Command
    if parsed['command'] == 'take':
        # Controller fragt Model: "Welches Item passt zu diesem Text?"
        match = self.model.find_matching_item(
            parsed['object_text'],
            parsed['adjectives']
        )
        # Model gibt zurück: {'item_id': 'schluessel', 'similarity': 0.89} oder None

        # 4. Controller: Entscheidung basierend auf Match-Qualität
        if match is None:
            self.view.show_message(f"Ich sehe hier kein {parsed['object_text']}.")
            return

        if match['similarity'] < 0.5:
            # Zu unsicher → Nachfragen
            self.view.show_message(f"Meinst du {match['name']}?")
            # (TODO: Bestätigung vom User abwarten)
            return

        # 5. Controller: Aktion ausführen via Model
        result = self.model.take_item(match['item_id'])

        # 6. Controller: View aktualisieren
        if result:
            self.view.show_message(f"Du nimmst {result['name']}.")
        else:
            self.view.show_message("Das kannst du nicht nehmen.")
```

**Verantwortlichkeiten klar getrennt:**
- **Parser:** Text verstehen (NLP)
- **Controller:** Entscheidungen treffen (zu unsicher? nachfragen!)
- **Model:** Daten finden und validieren (DB-Logik)

---

## Implementierung: SmartParser-Klasse

**Schnittstelle (GEÄNDERT - kein game_model mehr!):**
```python
class SmartParser:
    def __init__(self):
        """
        Lädt NLP-Modelle (SpaCy, SentenceTransformer)
        KEIN DB-Zugriff nötig!
        """
        self.nlp = spacy.load("de_dep_news_trf")
        self.sentence_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.command_embeddings = self._precompute_command_embeddings()

    def parse(self, input_text):
        """
        Hauptmethode - gibt strukturierte Parsing-Info zurück

        Args:
            input_text: User-Input (z.B. "Nimm den goldenen Schlüssel")

        Returns:
            dict: {
                'command': str,
                'confidence': float,
                'object_text': str,
                'adjectives': list,
                'raw': str,
                'verb_lemma': str
            }
        """
        # Layer 1: SpaCy NLP
        syntax = self._extract_syntax(input_text)

        # Layer 2: Verb → Command Matching
        command, confidence = self._verb_to_command(syntax['verb_lemma'])

        # Output formatieren (KEIN DB-Lookup!)
        return {
            'command': command,
            'confidence': confidence,
            'object_text': syntax['object_text'],
            'adjectives': syntax['adjectives'],
            'raw': input_text,
            'verb_lemma': syntax['verb_lemma']
        }
```

**Interne Methoden:**
```python
_extract_syntax(text)                    # Layer 1: SpaCy Parsing
_verb_to_command(verb_lemma)             # Layer 2: Embedding-Matching
_precompute_command_embeddings()         # Optimierung: Cache
```

**KEIN DB-Zugriff im Parser!**
- Keine Dependency auf `GameModel`
- Parser ist isoliert testbar (ohne Neo4j)
- Schneller Unit-Test möglich

---

## Model: Neue Methoden für Entity-Matching

**GameModel erweitern:**

```python
class GameModel:
    # ... bestehende Methoden ...

    def find_matching_item(self, item_text, adjectives=[], context='location'):
        """
        Findet Item basierend auf Text und optional Adjektiven

        Args:
            item_text: Objekt-Name vom Parser (z.B. "Schlüssel")
            adjectives: Liste von Adjektiven (z.B. ["goldenen"])
            context: 'location' (Items am Ort) oder 'inventory' (Items im Inventar)

        Returns:
            dict: {'item_id': str, 'name': str, 'similarity': float} oder None
        """
        # 1. DB-Abfrage: Hole Items (am Ort oder im Inventar)
        if context == 'location':
            query = """
                MATCH (p:Player {id: 'player'})-[:IST_IN]->(loc:Location)
                MATCH (i:Item)-[:IST_IN]->(loc)
                RETURN i.id as id, i.name as name, i.name_embedding as embedding
            """
        elif context == 'inventory':
            query = """
                MATCH (p:Player {id: 'player'})-[:TRÄGT]->(i:Item)
                RETURN i.id as id, i.name as name, i.name_embedding as embedding
            """

        items = self._run_query(query)

        if not items:
            return None

        # 2. Text kombinieren: "goldenen Schlüssel"
        search_text = ' '.join(adjectives + [item_text])

        # 3. Similarity berechnen (mit Sentence Transformer)
        search_embedding = self.sentence_model.encode(search_text)

        best_match = None
        best_similarity = 0.0

        for item in items:
            # Vector Similarity (Cosine)
            similarity = util.cos_sim(search_embedding, item['embedding'])[0][0].item()

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    'item_id': item['id'],
                    'name': item['name'],
                    'similarity': similarity
                }

        # 4. Validierung: Mindest-Schwellwert (z.B. 0.3)
        if best_similarity < 0.3:
            return None

        return best_match

    def find_matching_location(self, location_text, adjectives=[]):
        """
        Analog zu find_matching_item, aber für Locations
        Sucht nur in verbundenen Locations (via ERREICHT)
        """
        # Ähnliche Logik wie find_matching_item
        pass
```

**Model-Verantwortlichkeiten:**
- ✅ DB-Queries ausführen
- ✅ Embeddings vergleichen (Similarity)
- ✅ Business-Validierung (ist Item am Ort? ist es nehmbar?)
- ✅ Schwellwerte prüfen (z.B. min. 0.3 Similarity)

---

## Integration in bestehende Architektur

**Controller-Änderung:**
```python
# Alt:
self.parser = CommandParser()

# Neu:
self.parser = SmartParser()  # KEIN game_model mehr!

# parse()-Aufruf - Output-Format ändert sich!
parsed = self.parser.parse(command)
# → {'command': 'take', 'object_text': 'Schlüssel', 'adjectives': [...], ...}
```

**Model erweitern:**
- Neue Methoden: `find_matching_item()`, `find_matching_location()`
- Bestehende Methoden bleiben unverändert

**Controller process_command() umbauen:**
- Alte Logik: `if action == 'take': self.model.take_item(targets[0])`
- Neue Logik: Erst Model fragen (Matching), dann Aktion ausführen

**View:** Keine Änderungen

---

## Performance-Überlegungen

**Model Loading:**
- SpaCy TRF-Modell: ~500MB, Ladezeit ~2-5s
- Sentence Transformer: ~120MB, Ladezeit ~1s
- **Lösung:** Models beim Start laden (einmalig), dann im RAM halten

**Inference-Zeit:**
- SpaCy: ~50-100ms pro Satz
- Sentence Transformer (Verb-Matching): ~10-30ms
- Sentence Transformer (Entity-Matching im Model): ~10-30ms pro Item
- DB-Query: ~5-20ms
- **Gesamt:** ~100-200ms pro User-Input → Akzeptabel für Text-Adventure

**Optimierungen:**
- Command-Embeddings vorberechnen (Cache im Parser) ✅
- Item-Embeddings sind bereits in DB gespeichert ✅
- Kontext-Awareness reduziert Items zum Vergleichen (nur am Ort oder im Inventar)

---

## Architektur-Fragen (Entscheidungen dokumentiert)

### 1. Wo werden Command-Verb-Mappings gespeichert?
**Entscheidung:** Python-Dict im SmartParser (Option A)
- Flexibel, Code-nah
- Schnelle Iteration während Entwicklung
- Später migrierbar zu JSON/DB wenn nötig

### 2. Welche Entity-Resolution-Strategie?
**Roadmap:**
- **Phase 1:** Strategie 1 (Exaktes String-Matching mit Teilwort-Support)
- **Phase 2:** Strategie 3 (Embedding-basiert) - nutzt bereits vorhandene Embeddings!
- **Optional:** Strategie 2 (Fuzzy) als Fallback

### 3. Hat der Parser DB-Zugriff?
**Entscheidung:** NEIN!
- Parser = NLP-Layer (Text → Struktur)
- Model = Data-Layer (DB-Zugriff, Matching)
- Controller = Orchestration-Layer (verbindet Parser + Model)
- Klare Separation of Concerns (MVC-Pattern)

### 4. Multi-Command-Sätze?
"Nimm den Schlüssel und geh zur Taverne"
- **Phase 1:** Nicht unterstützt (nur 1 ROOT-Verb)
- **Future:** SpaCy findet koordinierte Verben (`cj`-Dependency) → Parser gibt Liste von Commands zurück

---

## Roadmap

**Phase 1 (MVP):**
- [x] SpaCy Syntax-Parsing testen (Notebook)
- [x] Sentence Transformer Verb-Matching implementieren (Notebook)
- [x] Test-Suite mit 40+ Testsätzen (Notebook)
- [ ] SmartParser-Klasse implementieren (ohne DB-Zugriff!)
- [ ] Model: find_matching_item() implementieren (Strategie 1: Exakt)
- [ ] Controller: process_command() umbauen (Parser → Model → View)
- [ ] Integration testen

**Phase 2 (Robustheit):**
- [ ] Model: Embedding-basiertes Matching (Strategie 3)
- [ ] Controller: Confidence-Thresholds und Fehlerbehandlung
- [ ] Controller: Nachfrage-System bei Ambiguität
- [ ] Trennbare Verben vollständig unterstützen

**Phase 3 (Advanced):**
- [ ] find_matching_location() für visit-Command
- [ ] Multi-Command-Parsing
- [ ] Context-Aware Disambiguation ("es" = letztes Objekt)
- [ ] Adjektiv-Matching optimieren (mehrere Adjektive)

---

## Testing-Strategie

**Parser (Unit-Tests ohne DB):**
```python
def test_parser_extract_verb():
    parser = SmartParser()
    result = parser.parse("Nimm den Schlüssel")
    assert result['command'] == 'take'
    assert result['object_text'] == 'Schlüssel'

def test_parser_adjectives():
    parser = SmartParser()
    result = parser.parse("Nimm den goldenen alten Schlüssel")
    assert result['adjectives'] == ['goldenen', 'alten']
```

**Model (Integration-Tests mit Test-DB):**
```python
def test_model_find_item():
    model = GameModel()
    match = model.find_matching_item("Schlüssel", ["goldenen"])
    assert match['item_id'] == 'schluessel'
    assert match['similarity'] > 0.7
```

**Controller (E2E-Tests):**
```python
def test_take_item_flow():
    controller = GameController()
    controller.process_command("Nimm den goldenen Schlüssel")
    # Prüfe: Item ist im Inventar
```

---

## Verwandte Dokumente

- `architecture_idea.md` - MVC-Pattern und ursprüngliche Vision
- `neo4j_cheatsheet.md` - Cypher-Query-Referenz
- `CLAUDE.md` - Projekt-Instruktionen und aktueller Stand
- `notebooks/03-smart-parser.ipynb` - Experimente und Tests

---

**Letzte Aktualisierung:** 4. Dezember 2024
**Status:** Architektur definiert - Ready for Implementation
**Version:** v2.0 (MVC-konform, Parser ohne DB-Zugriff)
