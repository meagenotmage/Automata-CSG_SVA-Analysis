## Subject–Verb Agreement (SVA) Visualizer — System Architecture

This document describes a suggested architecture for an SVA Visualizer built using a Context-Sensitive Grammar (CSG) architecture. It includes a high-level component breakdown, a text-based architecture diagram, the JSON API contract for parsing/validation, a worked example, and recommended next steps.

### High-Level Components

- Frontend (Visualizer UI)
  - User types sentences
  - Displays parse trees, grammar rules, and error highlights
  - Interactive controls to step through derivations

- Backend (API Server)
  - Handles grammar validation requests
  - Routes: `/parse`, `/validate`
  - Passes sentence tokens to the Grammar Engine

- Grammar Engine (Core Logic)
  - Implements Context-Sensitive Grammar rules
  - Runs derivations to check subject–verb agreement
  - Produces structured derivation steps and parse trees

- Visualizer Module
  - Generates dynamic parse trees or derivation sequences (D3.js recommended)
  - Interacts with the frontend via JSON or WebSocket updates

- Database (optional)
  - Store grammar rules, user-submitted sentences, and logs of derivations
  - SQLite or JSON-backed store are good lightweight options for prototypes


### Architecture Diagram (Text-Based Layout)

                ┌────────────────────────────────────┐
                │          Frontend (React)          │
                │  - User input sentence             │
                │  - Shows grammar & parse tree      │
                │  - Displays errors (SVA mismatch)  │
                └───────────────▲────────────────────┘
                                │
                                │ JSON Request (sentence)
                                ▼
                ┌────────────────────────────────────┐
                │        Backend API (Flask)         │
                │  - Routes: /parse, /validate       │
                │  - Handles HTTP requests           │
                │  - Passes data to Grammar Engine   │
                └───────────────▲────────────────────┘
                                │
                                │
                                ▼
                ┌────────────────────────────────────┐
                │       Grammar Engine (Python)       │
                │  - Context-Sensitive Grammar Rules  │
                │  - Parsing & derivation logic       │
                │  - Detects subject-verb mismatch    │
                │  - Returns structured result        │
                └───────────────▲────────────────────┘
                                │
                                │
                                ▼
                ┌────────────────────────────────────┐
                │      Visualizer Module (D3.js)     │
                │  - Builds parse tree dynamically   │
                │  - Highlights grammar flow         │
                └───────────────▲────────────────────┘
                                │
                                │
                                ▼
                ┌────────────────────────────────────┐
                │  Database (SQLite / JSON file)     │
                │  - Stores grammar rules            │
                │  - Logs user input & results       │
                └────────────────────────────────────┘


### Example Workflow (end-to-end)

1. Frontend (React UI)
   - User enters: “The cats runs.”

2. Backend (Flask API)
   - POST { "sentence": "The cats runs." } to `/parse`

3. Grammar Engine (Python)
   - Tokenizes: [The] [cats] [runs]
   - Applies context-sensitive rules
   - Detects number mismatch (plural noun + singular verb)

4. Backend returns JSON like (see `examples/parse_response.json`):

```json
{
  "status": "error",
  "message": "Subject–verb disagreement: 'cats' (plural) → 'runs' (singular)",
  "parse_tree": { /* abbreviated tree structure */ }
}
```

5. Visualizer (D3.js)
   - Renders a parse tree and highlights the VP node in red.


### Suggested API Contract

- POST /parse
  - Request: { "sentence": "..." }
  - Response (success):
    - status: "ok"
    - parse_tree: object (nodes/labels)
    - derivation: optional array of derivation steps
  - Response (error):
    - status: "error"
    - message: human-friendly error
    - problem_spans: list of spans (start, end, reason)


### Minimal File Structure (recommended)

```
automata/
├── backend/
│   ├── app.py                 # Flask app (routes /parse, /validate)
│   └── requirements.txt       # Flask + dependencies
├── grammar_engine/
│   └── engine.py              # CSG rules, tokenizer, derivations
├── frontend/
│   └── (React + D3 visualizer)
├── docs/
│   └── architecture.md        # (this file)
└── examples/
    └── parse_response.json    # sample API response
```


### Minimal Contract (2–4 bullets)

- Input: a UTF-8 sentence string.
- Output: JSON describing parse tree, derivation steps, and any SVA issues.
- Error modes: unparsable sentence, ambiguous grammar (provide alternatives), or detected SVA mismatch (explicit span + reason).


### Edge cases to handle

- Empty or whitespace-only input
- Punctuation-heavy sentences
- Coordination (e.g., "The cat and the dogs run") — requires careful number resolution
- Embedded clauses and relative pronouns
- Irregular verbs and agreement with collective nouns


### Next steps / Implementation roadmap

1. Implement a lightweight Flask backend with `/parse`.
2. Implement a small CSG-based grammar engine in `grammar_engine/engine.py` with tokenization and a simple set of rules for noun/verb number features.
3. Implement a React/D3 frontend to render parse trees and highlight problem nodes.
4. Add tests: unit tests for the grammar engine and an integration test for the API.
5. Optional: persist user examples and derivations in SQLite.


### Notes

- For initial prototypes, prefer an explicit, small rule set (100–200 lines) rather than a fully general CSG engine. That will make the derivations easier to show step-by-step in the visualizer.
- Keep the API stable and JSON-first — the frontend can subscribe for WebSocket updates later if you want live derivation stepping.

---

End of architecture overview.
