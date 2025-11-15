# AI-Textadventure - Setup & Installation

Ein textbasiertes Adventure-Game mit Neo4j GraphDB und Rich Terminal UI.

**Timeline:** 4 Wochen MVP, dann AI-Integration in v2  
**Tech-Stack:** Python, Neo4j, Rich, (später: Ollama)

---

## 📋 Voraussetzungen

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop/))
- **Git** (optional, für Versionskontrolle)

---

## 🚀 Installation

### 1. Docker Desktop installieren

**Windows/Mac:**
1. Download von https://www.docker.com/products/docker-desktop/
2. Installieren und starten
3. Testen: `docker --version`

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo systemctl start docker
```

### 2. Neo4j Container starten

```bash
# Container erstellen und starten
docker run -d \
    --name textadventure-neo4j \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    -v neo4j_data:/data \
    neo4j:latest
```

**Was passiert:**
- Port `7474`: Web UI → http://localhost:7474
- Port `7687`: Bolt Protocol (für Python)
- Volume `neo4j_data`: Daten bleiben bei Restart erhalten
- Login: `neo4j` / `password`

**Neo4j Browser testen:**
1. Öffne http://localhost:7474
2. Login: `neo4j` / `password`
3. Teste Query: `RETURN "Hello Neo4j" AS message`

### 3. Python Environment einrichten

```bash
# Repository klonen (oder Ordner erstellen)
git clone <repo-url>
cd textadventure

# Virtual Environment erstellen
python -m venv venv

# Aktivieren
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

**`requirements.txt`:**
```
rich>=13.0.0
neo4j>=5.0.0
python-dotenv>=1.0.0
jupyter>=1.0.0
```

### 4. Environment Variables konfigurieren

```bash
# .env Datei erstellen (aus Template)
cp .env.example .env

# .env bearbeiten und Credentials eintragen:
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

---

## 🗂️ Projektstruktur

```
textadventure/
├── src/
│   ├── controllers/
│   ├── models/
│   ├── views/
│   └── utils/
├── data/
├── notebooks/
├── docs/
```

---


## ✅ Definition of Done (MVP)

Das MVP ist fertig, wenn:

1. ✅ Spiel startet mit `python src/main.py`
2. ✅ Story "Die gestohlene Krone" ist durchspielbar
3. ✅ Alle Befehle funktionieren ohne Crashes
4. ✅ UI ist lesbar und strukturiert
5. ✅ Quest ist lösbar
6. ✅ Hilfe-Funktion erklärt alle Befehle
7. ✅ Code ist dokumentiert
8. ✅ README ist aktuell
9. ✅ Es macht Spaß zu spielen! 🎉

---

## 🚀 Nach dem MVP (v2+)

**Phase 2a - LLM Basics:**
- Ollama Integration
- Dynamische Raumbeschreibungen
- NPC-Dialoge mit LLM

**Phase 2b - Smart Parser:**
- Embeddings-Parser
- Natural Language Understanding

**Phase 2c - Advanced AI:**
- RAG für NPC-Wissen
- Story-Generator

**Phase 3 - Analytics:**
- Event-Logging (DuckDB)
- BI-Dashboard (Streamlit)

---

**Version:** MVP v1.0  
**Letzte Aktualisierung:** November 2025  
**Status:** In Entwicklung 🚧