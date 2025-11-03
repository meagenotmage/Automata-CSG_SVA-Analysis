import re
from typing import List, Dict, Any
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import extended features
from grammar_engine.extended_features import (
    PRONOUNS, IRREGULAR_VERBS, CONTRACTIONS, AUXILIARIES, COORDINATORS,
    INDEFINITE_PRONOUNS, COLLECTIVE_NOUNS, UNIT_WORDS, SINGULAR_PLURALS
)


def tokenize(sentence: str) -> List[Dict[str, Any]]:
    """Tokenizer that handles contractions like don't, isn't."""
    tokens = []
    # Enhanced pattern to capture contractions
    for m in re.finditer(r"\w+(?:'\w+)?|[^\s\w]", sentence):
        text = m.group(0)
        tokens.append({"text": text, "start": m.start(), "end": m.end()})
    return tokens


def get_number_for_noun(noun: str) -> str:
    """Determine if a noun is singular or plural.
    
    Implements SVA rules:
    - Rule 2: "I" and "you" take plural verbs
    - Rule 5: Indefinite pronouns are always singular
    - Rule 6: Collective nouns are usually singular
    - Rule 9: Titles, countries, and subjects like "mathematics" are singular
    """
    noun_l = noun.lower()
    
    # Rule 5: Indefinite pronouns are always singular
    if noun_l in INDEFINITE_PRONOUNS:
        return 'singular'
    
    # Check regular pronouns (includes Rule 2: "I" and "you" as plural)
    if noun_l in PRONOUNS:
        return PRONOUNS[noun_l]['number']
    
    # Rule 9: Subjects that look plural but are singular
    if noun_l in SINGULAR_PLURALS:
        return 'singular'
    
    # Rule 6: Collective nouns are singular (treated as one unit)
    if noun_l in COLLECTIVE_NOUNS:
        return 'singular'
    
    # Special cases for irregular plurals
    irregular_plurals = {'children', 'people', 'men', 'women', 'feet', 'teeth', 'mice'}
    if noun_l in irregular_plurals:
        return 'plural'
    
    # Crude heuristic: plural if ends with 's' and not possessive
    if noun_l.endswith('s') and not noun_l.endswith("'s"):
        return 'plural'
    
    return 'singular'


def get_number_for_verb(verb: str) -> str:
    """Determine if a verb form is singular or plural."""
    v = verb.lower()
    
    # Check contractions first (these are the FULL forms like "don't")
    if v in CONTRACTIONS:
        return CONTRACTIONS[v]
    
    # Check irregular verbs
    if v in IRREGULAR_VERBS:
        return IRREGULAR_VERBS[v][0]  # First element is the number
    
    # Fallback heuristic: verbs ending with 's' (except 'is', 'has', 'does') are singular
    if v.endswith('s'):
        return 'singular'
    
    return 'plural'


def find_verb_for_agreement(words: List[str], subject_index: int = 0) -> tuple:
    """Find the verb that should agree with the subject.
    
    Returns: (verb_text, is_auxiliary)
    
    Priority:
    1. Auxiliary verbs in contractions (don't, doesn't, isn't, aren't, etc.)
    2. Auxiliary verbs (do, does, is, are, has, have, was, were)
    3. Main verb (first verb after subject, not last word)
    """
    words_lower = [w.lower() for w in words]
    
    # Check for contractions with auxiliaries (don't, doesn't, etc.)
    for i, word in enumerate(words):
        w_lower = word.lower()
        if w_lower in CONTRACTIONS:
            # This is an auxiliary in contracted form
            return (word, True)
    
    # Check for standalone auxiliaries
    for i, word in enumerate(words):
        w_lower = word.lower()
        if w_lower in AUXILIARIES:
            return (word, True)
    
    # Find main verb - look for common verb forms after the subject
    common_verbs = {
        'run', 'runs', 'walk', 'walks', 'play', 'plays', 'eat', 'eats', 
        'sleep', 'sleeps', 'go', 'goes', 'come', 'comes', 'make', 'makes',
        'take', 'takes', 'get', 'gets', 'see', 'sees', 'know', 'knows',
        'think', 'thinks', 'give', 'gives', 'find', 'finds', 'tell', 'tells',
        'work', 'works', 'call', 'calls', 'try', 'tries', 'ask', 'asks',
        'need', 'needs', 'feel', 'feels', 'become', 'becomes', 'leave', 'leaves',
        'put', 'puts', 'mean', 'means', 'keep', 'keeps', 'let', 'lets',
        'begin', 'begins', 'seem', 'seems', 'help', 'helps', 'talk', 'talks',
        'turn', 'turns', 'start', 'starts', 'show', 'shows', 'hear', 'hears',
        'move', 'moves', 'like', 'likes', 'live', 'lives', 'believe', 'believes',
        'hold', 'holds', 'bring', 'brings', 'happen', 'happens', 'write', 'writes',
        'sit', 'sits', 'stand', 'stands', 'lose', 'loses', 'pay', 'pays',
        'meet', 'meets', 'include', 'includes', 'continue', 'continues',
        'set', 'sets', 'learn', 'learns', 'change', 'changes', 'lead', 'leads',
        'understand', 'understands', 'watch', 'watches', 'follow', 'follows',
        'stop', 'stops', 'create', 'creates', 'speak', 'speaks', 'read', 'reads',
        'spend', 'spends', 'grow', 'grows', 'open', 'opens', 'win', 'wins',
        'teach', 'teaches', 'offer', 'offers', 'remember', 'remembers',
        'consider', 'considers', 'appear', 'appears', 'buy', 'buys', 'wait', 'waits',
        'serve', 'serves', 'die', 'dies', 'send', 'sends', 'build', 'builds',
        'stay', 'stays', 'fall', 'falls', 'cut', 'cuts', 'reach', 'reaches',
        'kill', 'kills', 'raise', 'raises', 'pass', 'passes', 'sell', 'sells',
        'decide', 'decides', 'return', 'returns', 'explain', 'explains',
        'hope', 'hopes', 'develop', 'develops', 'carry', 'carries', 'break', 'breaks'
    }
    
    # Look for first verb after subject position
    for i in range(subject_index, len(words)):
        w_lower = words[i].lower()
        if w_lower in common_verbs or w_lower in IRREGULAR_VERBS:
            return (words[i], False)
    
    # Fall back: use the word after subject if it looks like a verb (ends in common verb suffixes)
    if len(words) > subject_index + 1:
        next_word = words[subject_index + 1]
        w_lower = next_word.lower()
        # Check if it looks like a verb (doesn't end with 'ly', 'tion', 'ness', etc.)
        if not any(w_lower.endswith(suffix) for suffix in ['ly', 'tion', 'ness', 'ment', 'ing', 'ed']):
            return (next_word, False)
    
    # Last resort: last word
    if words:
        return (words[-1], False)
    
    return (None, False)


def get_correct_verb_form(verb: str, target_number: str) -> str:
    """Get the correct verb form for the target number."""
    v_lower = verb.lower()
    
    # Handle contractions
    if v_lower in CONTRACTIONS:
        if target_number == 'singular':
            return "doesn't" if "do" in v_lower else "isn't" if "is" in v_lower or "are" in v_lower else "wasn't" if "was" in v_lower or "were" in v_lower else "hasn't" if "has" in v_lower or "have" in v_lower else verb
        else:  # plural
            return "don't" if "do" in v_lower else "aren't" if "is" in v_lower or "are" in v_lower else "weren't" if "was" in v_lower or "were" in v_lower else "haven't" if "has" in v_lower or "have" in v_lower else verb
    
    # Handle irregular verbs
    if v_lower in IRREGULAR_VERBS:
        current_number = IRREGULAR_VERBS[v_lower][0]
        if current_number != target_number:
            # Return the opposite form
            return IRREGULAR_VERBS[v_lower][1]
    
    # Handle regular verbs
    if target_number == 'singular':
        if not v_lower.endswith('s'):
            return verb + 's'
    else:  # plural
        if v_lower.endswith('s') and v_lower not in {'is', 'has', 'does', 'was'}:
            return verb[:-1]
    
    return verb


def detect_compound_subject(words: List[str]) -> tuple:
    """Detect compound subjects joined by 'and', 'or', or 'nor'.
    
    Returns: (has_compound, coordinator, subjects, compound_number)
    
    Rule 3: Subjects joined by "and" → plural verb
    Rule 4: Subjects joined by "or"/"nor" → verb agrees with nearest subject
    """
    # Look for coordinators
    for i, word in enumerate(words):
        w_lower = word.lower()
        if w_lower in {'and', 'or', 'nor'}:
            # Found a coordinator - check if it's between two nouns
            if i > 0 and i < len(words) - 1:
                # Get words before and after coordinator
                before = words[i-1]
                after_idx = i + 1
                
                # Skip determiners after coordinator
                while after_idx < len(words) and words[after_idx].lower() in {'the', 'a', 'an'}:
                    after_idx += 1
                
                if after_idx < len(words):
                    after = words[after_idx]
                    
                    # Rule 3: "and" makes subject plural
                    if w_lower == 'and':
                        return (True, 'and', [before, after], 'plural')
                    
                    # Rule 4: "or" or "nor" → verb agrees with nearest subject
                    elif w_lower in {'or', 'nor'}:
                        nearest_number = get_number_for_noun(after)
                        return (True, w_lower, [before, after], nearest_number)
    
    return (False, None, [], None)


def build_parse_tree(tokens: List[Dict[str, Any]], noun_token, verb_token) -> Dict[str, Any]:
    """Build a simple parse tree structure."""
    # Build NP children, filtering out None values
    np_children = []
    if tokens and len(tokens) >= 1 and tokens[0]['text'].lower() in {'the', 'a', 'an'}:
        np_children.append({'label': 'DET', 'text': tokens[0]['text']})
    np_children.append({'label': 'N', 'text': noun_token['text'], 'features': noun_token['features']})
    
    return {
        'label': 'S',
        'children': [
            {
                'label': f"NP ({noun_token['features']['number']})",
                'children': np_children
            },
            {
                'label': f"VP ({verb_token['features']['number']})",
                'children': [
                    {'label': 'V', 'text': verb_token['text'], 'features': verb_token['features']}
                ]
            }
        ]
    }


def analyze(sentence: str) -> Dict[str, Any]:
    """Analyze sentence and return a JSON-serializable dict describing SVA issues.
    
    Key improvements:
    - Handles contractions (don't, doesn't, isn't, aren't)
    - Prioritizes auxiliary verbs for agreement checking
    - Supports pronouns (I, you, he, she, it, we, they)
    """
    tokens = tokenize(sentence)
    words = [t['text'] for t in tokens if re.match(r"\w+(?:'\w+)?", t['text'])]
    
    if not words:
        return {'status': 'error', 'message': 'Unable to parse sentence (too short or not supported).'}
    
    # Find the subject noun (first non-determiner word)
    dets = {'the', 'a', 'an'}
    possessives = {'my', 'your', 'his', 'her', 'its', 'our', 'their'}
    noun = None
    
    for i, w in enumerate(words):
        w_lower = w.lower()
        
        # Skip determiners
        if w_lower in dets:
            continue
            
        # Skip possessive pronouns - look at next word
        if w_lower in possessives:
            continue
        
        # Skip verbs and auxiliaries when looking for subject
        if w_lower not in AUXILIARIES and w_lower not in CONTRACTIONS:
            # Check if it's a known verb form
            if w_lower not in {'run', 'runs', 'walk', 'walks', 'play', 'plays', 'eat', 'eats', 'sleep', 'sleeps'}:
                noun = w
                break
            # If it could be a verb, check if it's the first word (then it might be imperative)
            if i > 0:
                noun = w
                break
    
    # If still no noun found, try first non-possessive word
    if noun is None:
        for w in words:
            if w.lower() not in dets and w.lower() not in possessives:
                noun = w
                break
    
    # Last resort
    if noun is None:
        noun = words[0]
    
    # Check for compound subjects (Rule 3 & 4)
    has_compound, coordinator, compound_subjects, compound_number = detect_compound_subject(words)
    
    if has_compound:
        # Use compound number for agreement
        noun_feats = {'number': compound_number}
        # Update noun to show both subjects
        noun = f"{compound_subjects[0]} {coordinator} {compound_subjects[1]}"
    else:
        # Single subject
        noun_feats = {'number': get_number_for_noun(noun)}
    
    # Get subject index for verb detection
    subject_index = words.index(noun) if noun in words else 0
    
    # Find the verb that should agree with the subject
    verb, is_auxiliary = find_verb_for_agreement(words, subject_index)
    
    if verb is None:
        return {'status': 'error', 'message': 'Unable to parse sentence (no verb found).'}
    
    # Get verb features
    verb_feats = {'number': get_number_for_verb(verb)}
    
    # Find token dicts for noun and verb for offsets
    noun_token = next((t for t in tokens if t['text'].lower() == noun.lower()), {'text': noun, 'start': 0, 'end': len(noun)})
    verb_token = next((t for t in tokens if t['text'].lower() == verb.lower()), {'text': verb, 'start': 0, 'end': len(verb)})
    noun_token['features'] = noun_feats
    verb_token['features'] = verb_feats
    
    # Check agreement
    problem_spans = []
    status = 'ok'
    message = 'Subject-verb agreement is correct.'
    suggested_sentence = None
    
    if noun_feats['number'] != verb_feats['number']:
        status = 'error'
        aux_note = " (auxiliary)" if is_auxiliary else ""
        message = f"Subject-verb disagreement: '{noun}' ({noun_feats['number']}) does not agree with '{verb}' ({verb_feats['number']}){aux_note}"
        
        # Generate suggested correction
        correct_verb = get_correct_verb_form(verb, noun_feats['number'])
        suggested_sentence = sentence.replace(verb, correct_verb)
        
        problem_spans = [
            {
                'type': 'subject',
                'text': noun_token['text'],
                'start': noun_token.get('start', 0),
                'end': noun_token.get('end', 0),
                'features': noun_feats,
                'subject_features': noun_feats,
                'verb_features': verb_feats
            }
        ]
    
    parse_tree = build_parse_tree(tokens, noun_token, verb_token)
    
    result = {
        'status': status,
        'message': message,
        'problem_spans': problem_spans,
        'parse_tree': parse_tree,
        'derivation': []  # Placeholder for future derivation steps
    }
    
    # Add suggested correction if there's an error
    if suggested_sentence:
        result['suggested_correction'] = suggested_sentence
    
    return result


if __name__ == '__main__':
    # Manual tests
    import json
    
    test_sentences = [
        "The cats runs.",           # ERROR: plural noun, singular verb
        "The cat runs.",            # OK: singular noun, singular verb
        "They don't run.",          # OK: plural pronoun, plural auxiliary (don't)
        "He doesn't run.",          # OK: singular pronoun, singular auxiliary (doesn't)
        "They doesn't run.",        # ERROR: plural pronoun, singular auxiliary
        "The children plays.",      # ERROR: plural noun, singular verb
    ]
    
    for sent in test_sentences:
        print(f"\n{'='*60}")
        print(f"Sentence: {sent}")
        result = analyze(sent)
        print(json.dumps(result, indent=2))
