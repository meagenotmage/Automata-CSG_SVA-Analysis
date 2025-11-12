from grammar_engine.csg_engine import analyze

test_cases = [
    'maluche runs and kyla run',        # Should be ERROR
    'maluche runs and kyla runs',       # Should be OK
    'Maluche runs and Kyla run',        # Should be ERROR  
    'Maluche runs and Kyla runs',       # Should be OK
    'tom runs and mary walk',           # Should be ERROR
    'tom runs and mary walks',          # Should be OK
]

print('='*70)
print('Compound Sentence Tests (lowercase and capitalized)')
print('='*70)

for sentence in test_cases:
    result = analyze(sentence)
    status_icon = '✅' if result['status'] == 'ok' else '❌'
    
    print(f"\n{status_icon} {sentence}")
    print(f"   Status: {result['status'].upper()}")
    
    if result.get('suggested_correction'):
        print(f"   Correction: {result['suggested_correction']}")

print('\n' + '='*70)
