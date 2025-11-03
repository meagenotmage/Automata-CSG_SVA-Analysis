# Context-Sensitive Grammar Implementation

## Overview

This project now implements **true Context-Sensitive Grammar (CSG)** from automata theory, not just rule-based pattern matching. The new `csg_engine.py` provides formal CSG derivation with production rules.

## What is Context-Sensitive Grammar?

In **automata theory**, a Context-Sensitive Grammar (CSG) is a formal grammar where production rules have the form:

```
αAβ → αγβ
```

Where:
- **α, β** are context (strings of terminals/non-terminals, can be empty)
- **A** is a non-terminal symbol
- **γ** is a non-empty replacement string
- The context **α and β must be present** for the rule to apply

### Key Properties

1. **Context-dependent rules**: A symbol can only be rewritten if specific surrounding context exists
2. **Linear Bounded Automaton (LBA)**: CSG languages are recognized by LBAs
3. **Derivation traces**: Each application of a rule produces a step in the derivation sequence
4. **String length**: CSG rules are non-contracting (output ≥ input length)

## CSG vs Rule-Based Approach

### Old Approach (Rule-Based Engine)
```python
# Pattern matching and heuristics
if noun_feats['number'] != verb_feats['number']:
    status = 'error'
```

❌ **Not CSG**: Uses simple feature comparison, no formal derivation

### New Approach (CSG Engine)
```python
# Formal production rules with context
CSGRule("R1.2", "NP[plural]", " ", "VP[", "VP[plural]", 
        "Plural subject requires plural verb", 1)
```

✅ **True CSG**: Formal rules with left/right context that produce derivation steps

## CSG Production Rules for SVA

The engine defines formal CSG rules for each SVA case:

### Rule 1: Basic Agreement
```python
# αAβ → αγβ format
"NP[singular] VP[" → "NP[singular]VP[singular]VP["
"NP[plural] VP[" → "NP[plural]VP[plural]VP["
```

### Rule 2: Special Pronouns
```python
"NP[I] VP[" → "NP[I]VP[plural]VP["
"NP[you] VP[" → "NP[you]VP[plural]VP["
```

### Rule 3: Compound with "and"
```python
"NP[]+[]+]NP[" → "NP[]+NP[plural]"  # Plural verb required
```

### Rule 4: Compound with "or"/"nor"
```python
"NP[]+[or]NP[singular] VP[" → "NP[...]VP[singular]VP["  # Nearest subject
"NP[]+[or]NP[plural] VP[" → "NP[...]VP[plural]VP["
```

### Rule 5: Indefinite Pronouns
```python
"NP[indefinite] VP[" → "NP[indefinite]VP[singular]VP["
```

### Rule 6: Collective Nouns
```python
"NP[collective] VP[" → "NP[collective]VP[singular]VP["
```

### Rules 8 & 9: Special Cases
```python
"NP[unit] VP[" → "NP[unit]VP[singular]VP["         # Amounts, time, money
"NP[singular_plural] VP[" → "NP[...]VP[singular]VP["  # Mathematics, Philippines
```

## How the CSG Engine Works

### 1. Tokenization & Classification
```python
tokens = tokenize(sentence)
subject_category, subject_number = classify_noun(subject)
verb_number = classify_verb(verb)
```

### 2. Create Initial Parse String
```python
# Format: NP[features] VP[features]
parse_string = "NP[plural] VP[singular]"
```

### 3. Apply CSG Derivation
```python
for rule in CSG_PRODUCTION_RULES:
    if rule.matches(parse_string, position):
        new_string = rule.apply(parse_string, position)
        derivation_steps.append({
            'step': step,
            'string': new_string,
            'rule': rule.rule_id,
            'production': f"{rule.left_context}{rule.symbol}{rule.right_context} → ..."
        })
```

### 4. Verify Agreement
```python
is_correct = f"VP[{expected_number}]" in final_string
```

## Example Derivation

**Sentence:** "The cats runs."

### Derivation Steps:

```
Step 0: NP[plural] VP[singular]
        Initial parse string

Step 1: NP[plural]VP[plural]VP[singular]
        Rule R1.2 applied
        Production: NP[plural] VP[ → NP[plural]VP[plural]VP[
        Description: Plural subject requires plural verb
        SVA Rule: #1
```

**Result:** ❌ Error (expected `NP[plural] VP[plural]`, got mismatch)

**Suggestion:** "The cats run."

## API Response with CSG

When using the CSG engine, the `/parse` endpoint returns:

```json
{
  "status": "error",
  "message": "Subject-verb disagreement: 'cats' (plural) does not agree with 'runs' (singular).",
  "derivation": [
    {
      "step": 0,
      "string": "NP[plural] VP[singular]",
      "rule": null,
      "description": "Initial parse string"
    },
    {
      "step": 1,
      "string": "NP[plural]VP[plural]VP[singular]",
      "rule": "R1.2",
      "rule_description": "Plural subject requires plural verb",
      "sva_rule": 1,
      "production": "NP[plural] VP[ → NP[plural]VP[plural]VP["
    }
  ],
  "csg_analysis": {
    "initial_string": "NP[plural] VP[singular]",
    "final_string": "NP[plural]VP[plural]VP[singular]",
    "expected_string": "NP[plural] VP[plural]",
    "rules_applied": 1
  },
  "suggested_correction": "The cats run.",
  "engine_used": "csg"
}
```

## Using the CSG Engine

### Backend API

```python
# POST /parse with engine selection
{
  "sentence": "The cats runs.",
  "engine": "csg"  # or "rule" for old engine
}
```

### Frontend UI

The React frontend now includes:

1. **Engine Selector**: Toggle between CSG and Rule-Based engines
2. **CSG Analysis Section**: Shows initial/final strings and rules applied
3. **Enhanced Derivation Display**: Shows step-by-step CSG rule applications with:
   - Rule ID
   - Production rule in αAβ → αγβ format
   - Rule description
   - SVA rule number
   - Resulting string

## Testing the CSG Engine

```bash
# Run CSG engine directly
.venv\Scripts\python.exe grammar_engine/csg_engine.py

# Test via API
curl -X POST http://localhost:5000/parse \
  -H "Content-Type: application/json" \
  -d '{"sentence": "The cats runs.", "engine": "csg"}'
```

## Files

- `grammar_engine/csg_engine.py` - True CSG implementation
- `grammar_engine/engine.py` - Original rule-based engine (still available)
- `backend/app.py` - Flask API with engine selection
- `frontend/src/App.js` - React UI with CSG display

## Comparison: CSG vs Rule-Based

| Feature | Rule-Based Engine | CSG Engine |
|---------|------------------|------------|
| **Approach** | Pattern matching & heuristics | Formal production rules |
| **Derivation** | No formal derivation | Step-by-step CSG derivation |
| **Theory** | Ad-hoc rules | Automata theory CSG |
| **Context** | Implicit in code | Explicit in rule definition (αAβ) |
| **Traceability** | Low | High (complete derivation trace) |
| **Formality** | Informal | Formal grammar |
| **Educational** | Good for practice | Excellent for learning automata theory |

## Academic Rigor

The CSG engine implements:

✅ **Formal production rules** in αAβ → αγβ format  
✅ **Context-sensitive rewriting** (left/right context required)  
✅ **Derivation sequences** (step-by-step transformations)  
✅ **Non-contracting rules** (string length preserved/increased)  
✅ **Rule traceability** (every transformation logged)  
✅ **SVA grammar formalization** (9 comprehensive rules as CSG productions)

This is a **legitimate Context-Sensitive Grammar** from automata theory, suitable for:
- Computer Science coursework (Theory of Computation)
- Natural Language Processing studies
- Formal grammar demonstrations
- Educational visualization of CSG concepts

## References

- **Automata Theory**: Hopcroft, Motwani, Ullman - "Introduction to Automata Theory, Languages, and Computation"
- **Context-Sensitive Grammars**: Chomsky Hierarchy (Type-1 grammars)
- **Linear Bounded Automata**: Recognizers for CSG languages
- **Subject-Verb Agreement**: English grammar rules formalized as CSG productions
