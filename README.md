# SVA Visualizer (Context-Sensitive Grammar)

A Subject–Verb Agreement (SVA) Visualizer using Context-Sensitive Grammar with Flask backend, Python grammar engine, and React + D3 frontend.

## Features

- **Grammar Engine** — Tokenization, pronoun/irregular verb support, auxiliaries, coordination
- **Rule Tracing** — Step-by-step derivation display for educational purposes
- **Flask API** — RESTful backend with `/parse` endpoint
- **React Frontend** — Interactive UI with D3.js parse tree visualization
- **Comprehensive Tests** — Unit tests and integration tests with pytest

## Project Structure

```
automata/
├── backend/
│   ├── app.py                      # Flask API server
│   └── requirements.txt            # Python dependencies
├── grammar_engine/
│   ├── engine.py                   # CSG-based analyzer
│   └── extended_features.py        # Feature lookups (pronouns, auxiliaries, etc.)
├── frontend/
│   ├── src/
│   │   ├── App.js                  # Main React component
│   │   ├── components/
│   │   │   ├── ParseTreeVisualizer.js   # D3 tree visualization
│   │   │   └── DerivationSteps.js       # Derivation step display
│   │   └── ...
│   ├── package.json                # Node dependencies
│   └── README.md                   # Frontend setup guide
├── tests/
│   ├── test_engine.py              # Unit tests for grammar engine
│   └── test_integration.py         # Integration tests for Flask API
├── docs/
│   └── architecture.md             # Architecture overview
└── examples/
    └── parse_response.json         # Example API response
```

## Quick Start

### Backend Setup

```powershell
# Install dependencies
-m pip install -r backend/requirements.txt

# Run the Flask server
backend/app.py
```

Server runs on `http://localhost:5000`

### Frontend Setup

```powershell
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000` (proxied to backend)

### Run Tests

```powershell
# Run all tests
-m pytest -v

# Run unit tests only
-m pytest tests/test_engine.py -v

# Run integration tests only
-m pytest tests/test_integration.py -v
```

## API Usage

### POST /parse

**Request:**
```json
{
  "sentence": "The cats runs."
}
```

**Response:**
```json
{
  "status": "error",
  "message": "Subject–verb disagreement: 'cats' (plural) → 'runs' (singular)",
  "problem_spans": [...],
  "parse_tree": {...},
  "derivation": [...]
}
```

## Example Sentences

- "The cats runs." → Plural/singular mismatch
- "The cat and the dog runs." → Coordination issue
- "They don't run." → Contractions and pronouns
- "He runs fast." → Correct agreement ✓
- "The children plays." → Irregular plural mismatch

## Technologies

- **Backend:** Python 3.13, Flask 3.1
- **Grammar Engine:** Context-Sensitive Grammar with rule tracing
- **Frontend:** React 18, D3.js 7, Axios
- **Testing:** pytest 8.4

## Documentation

- [Architecture Overview](docs/architecture.md) — System design, API contract, roadmap
- [Frontend README](frontend/README.md) — React app setup and usage

## Next Steps

See `docs/architecture.md` for implementation roadmap and edge cases.
