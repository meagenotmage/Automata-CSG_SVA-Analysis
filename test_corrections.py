from grammar_engine.csg_engine import analyze

test_sentences = [
    'The cats runs.',
    'He watches movies.',
    'I work and they plays.',
    'The cat runs but the dogs barks.',
    'She sings and he dances.'
]

print('='*70)
print('CSG Engine - Sentence Corrections')
print('='*70)

for i, sentence in enumerate(test_sentences, 1):
    print(f'\n{i}. Input: {sentence}')
    result = analyze(sentence)
    
    if result['status'] == 'error':
        print(f'   Status: ❌ Error')
        print(f'   Original: {result.get("original_sentence")}')
        print(f'   Corrected: {result.get("suggested_correction")}')
    else:
        print(f'   Status: ✅ Correct')
    
    if result.get('is_compound'):
        print(f'   Type: Compound sentence ({result.get("clause_count")} clauses)')

print('\n' + '='*70)
