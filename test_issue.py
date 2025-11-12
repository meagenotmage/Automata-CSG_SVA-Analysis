from grammar_engine.csg_engine import analyze

sentence = 'maluche runs and kyla run'
result = analyze(sentence)

print(f"Sentence: {sentence}")
print(f"Status: {result['status']}")
print(f"Is Compound: {result.get('is_compound')}")
print(f"Clause Count: {result.get('clause_count')}")
print(f"Message: {result.get('message')}")

if result.get('is_compound'):
    print("\nClause analyses:")
    for clause in result.get('clause_analyses', []):
        print(f"  Clause {clause['clause_number']}: {clause['text']}")
        print(f"    Status: {clause['analysis']['status']}")
        print(f"    Message: {clause['analysis']['message']}")

if result.get('suggested_correction'):
    print(f"\nSuggested correction: {result['suggested_correction']}")
