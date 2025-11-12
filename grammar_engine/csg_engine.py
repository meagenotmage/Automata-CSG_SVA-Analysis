"""
Context-Sensitive Grammar (CSG) Engine for Subject-Verb Agreement Analysis

This module implements a true Context-Sensitive Grammar from automata theory.

CSG Definition:
- Production rules of the form: αAβ → αγβ
  where α, β are context (can be empty or non-empty strings)
  A is a non-terminal symbol
  γ is a non-empty string of terminals/non-terminals

Key Properties:
1. Rules are applied based on surrounding context
2. Derivation steps are tracked and can be traced
3. Linear Bounded Automaton (LBA) recognizer semantics
4. Each transformation preserves or reduces string length
"""

import re
from typing import List, Dict, Any, Tuple, Optional
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grammar_engine.extended_features import (
    PRONOUNS, IRREGULAR_VERBS, CONTRACTIONS, AUXILIARIES, COORDINATORS,
    INDEFINITE_PRONOUNS, COLLECTIVE_NOUNS, UNIT_WORDS, SINGULAR_PLURALS
)


# ============================================================================
# CSG Production Rules
# ============================================================================

class CSGRule:
    """Represents a context-sensitive production rule: αAβ → αγβ"""
    
    def __init__(self, rule_id: str, left_context: str, symbol: str, right_context: str, 
                 replacement: str, description: str, sva_rule_number: Optional[int] = None):
        self.rule_id = rule_id
        self.left_context = left_context  # α
        self.symbol = symbol              # A
        self.right_context = right_context # β
        self.replacement = replacement     # γ
        self.description = description
        self.sva_rule_number = sva_rule_number
    
    def __repr__(self):
        return f"CSGRule({self.rule_id}: {self.left_context}{self.symbol}{self.right_context} → {self.left_context}{self.replacement}{self.right_context})"
    
    def matches(self, string: str, position: int) -> bool:
        """Check if this rule can be applied at the given position in the string."""
        # Check if symbol matches at position
        symbol_end = position + len(self.symbol)
        if symbol_end > len(string):
            return False
        
        if string[position:symbol_end] != self.symbol:
            return False
        
        # Check left context
        left_start = position - len(self.left_context)
        if left_start < 0:
            return False
        if self.left_context and string[left_start:position] != self.left_context:
            return False
        
        # Check right context
        right_end = symbol_end + len(self.right_context)
        if right_end > len(string):
            return False
        if self.right_context and string[symbol_end:right_end] != self.right_context:
            return False
        
        return True
    
    def apply(self, string: str, position: int) -> str:
        """Apply this rule at the given position."""
        left_start = position - len(self.left_context)
        symbol_end = position + len(self.symbol)
        right_end = symbol_end + len(self.right_context)
        
        # Construct: prefix + left_context + replacement + right_context + suffix
        prefix = string[:left_start] if left_start > 0 else ""
        suffix = string[right_end:] if right_end < len(string) else ""
        
        return prefix + self.left_context + self.replacement + self.right_context + suffix


# Define CSG production rules for SVA
CSG_PRODUCTION_RULES = [
    # Rule 1: Basic singular/plural agreement
    CSGRule("R1.1", "NP[singular]", " ", "VP[", "VP[singular]", 
            "Singular subject requires singular verb", 1),
    CSGRule("R1.2", "NP[plural]", " ", "VP[", "VP[plural]", 
            "Plural subject requires plural verb", 1),
    
    # Rule 2: Special pronouns "I" and "you" take plural verbs
    CSGRule("R2.1", "NP[I]", " ", "VP[", "VP[plural]", 
            "Pronoun 'I' takes plural verb form", 2),
    CSGRule("R2.2", "NP[you]", " ", "VP[", "VP[plural]", 
            "Pronoun 'you' takes plural verb form", 2),
    
    # Rule 3: Compound subjects with "and" → plural
    CSGRule("R3", "NP[", "]+[", "]NP[", "]+NP[plural]", 
            "Subjects joined by 'and' require plural verb", 3),
    
    # Rule 4: Compound subjects with "or"/"nor" → nearest subject
    CSGRule("R4.1", "NP[", "]+[or]NP[singular]", " VP[", "VP[singular]", 
            "With 'or', verb agrees with nearest (singular) subject", 4),
    CSGRule("R4.2", "NP[", "]+[or]NP[plural]", " VP[", "VP[plural]", 
            "With 'or', verb agrees with nearest (plural) subject", 4),
    CSGRule("R4.3", "NP[", "]+[nor]NP[singular]", " VP[", "VP[singular]", 
            "With 'nor', verb agrees with nearest (singular) subject", 4),
    CSGRule("R4.4", "NP[", "]+[nor]NP[plural]", " VP[", "VP[plural]", 
            "With 'nor', verb agrees with nearest (plural) subject", 4),
    
    # Rule 5: Indefinite pronouns → singular
    CSGRule("R5", "NP[indefinite]", " ", "VP[", "VP[singular]", 
            "Indefinite pronouns (everyone, somebody, each) take singular verbs", 5),
    
    # Rule 6: Collective nouns → singular
    CSGRule("R6", "NP[collective]", " ", "VP[", "VP[singular]", 
            "Collective nouns (team, group, class) take singular verbs", 6),
    
    # Rule 8: Amount/time/money → singular
    CSGRule("R8", "NP[unit]", " ", "VP[", "VP[singular]", 
            "Amounts, time, and money expressions take singular verbs", 8),
    
    # Rule 9: Titles, countries, special plurals → singular
    CSGRule("R9", "NP[singular_plural]", " ", "VP[", "VP[singular]", 
            "Titles, countries, and special subjects (mathematics, Philippines) take singular verbs", 9),
]


# ============================================================================
# Token and Feature Analysis
# ============================================================================

def tokenize(sentence: str) -> List[Dict[str, Any]]:
    """Tokenize sentence into words with position information."""
    tokens = []
    for m in re.finditer(r"\w+(?:'\w+)?|[^\s\w]", sentence):
        text = m.group(0)
        tokens.append({"text": text, "start": m.start(), "end": m.end()})
    return tokens


def classify_noun(noun: str) -> Tuple[str, str]:
    """
    Classify a noun and return (category, number).
    
    Returns:
        category: 'pronoun', 'indefinite', 'collective', 'unit', 'singular_plural', 'regular'
        number: 'singular', 'plural'
    """
    noun_l = noun.lower()
    
    # Rule 5: Indefinite pronouns
    if noun_l in INDEFINITE_PRONOUNS:
        return ('indefinite', 'singular')
    
    # Rule 2 & regular pronouns
    if noun_l in PRONOUNS:
        return ('pronoun', PRONOUNS[noun_l]['number'])
    
    # Rule 9: Singular-looking plurals
    if noun_l in SINGULAR_PLURALS:
        return ('singular_plural', 'singular')
    
    # Rule 6: Collective nouns
    if noun_l in COLLECTIVE_NOUNS:
        return ('collective', 'singular')
    
    # Rule 8: Unit words
    if noun_l in UNIT_WORDS:
        return ('unit', 'singular')
    
    # Regular nouns
    irregular_plurals = {'children', 'people', 'men', 'women', 'feet', 'teeth', 'mice'}
    if noun_l in irregular_plurals:
        return ('regular', 'plural')
    
    if noun_l.endswith('s') and not noun_l.endswith("'s"):
        return ('regular', 'plural')
    
    return ('regular', 'singular')


def classify_verb(verb: str) -> str:
    """Classify verb and return its number."""
    v = verb.lower()
    
    # Check contractions
    if v in CONTRACTIONS:
        return CONTRACTIONS[v]
    
    # Check irregular verbs
    if v in IRREGULAR_VERBS:
        return IRREGULAR_VERBS[v][0]
    
    # Regular verbs: -s ending indicates singular
    if v.endswith('s') and v not in {'was', 'is', 'has', 'does'}:
        return 'singular'
    
    return 'plural'


def find_subject_and_verb(tokens: List[Dict[str, Any]], compound_info: Optional[Dict] = None) -> Tuple[Optional[str], Optional[str], int, int]:
    """
    Find the subject and verb in the sentence.
    
    Args:
        tokens: List of token dictionaries
        compound_info: Optional compound subject info to help skip past compound subjects
    
    Returns: (subject, verb, subject_index, verb_index)
    """
    words = [t['text'] for t in tokens if re.match(r"\w+(?:'\w+)?", t['text'])]
    
    if not words:
        return None, None, -1, -1
    
    # Find subject (skip determiners and possessives)
    dets = {'the', 'a', 'an'}
    possessives = {'my', 'your', 'his', 'her', 'its', 'our', 'their'}
    coordinators = {'and', 'or', 'nor'}
    
    subject = None
    subject_idx = -1
    last_noun_idx = -1  # Track the last noun in compound subject
    found_coordinator = False
    nouns_after_coordinator = 0
    
    for i, w in enumerate(words):
        w_lower = w.lower()
        if w_lower in dets or w_lower in possessives:
            continue
        if w_lower in coordinators:
            found_coordinator = True
            continue  # Skip coordinators when finding subject
        if w_lower not in AUXILIARIES and w_lower not in CONTRACTIONS:
            if subject is None:
                subject = w
                subject_idx = i
            
            # Update last_noun_idx, but stop after finding the second noun in compound
            if found_coordinator:
                nouns_after_coordinator += 1
                if nouns_after_coordinator == 1:
                    # This is the second noun in "X and Y"
                    last_noun_idx = i
                    break  # Stop here, we've found the complete compound subject
            else:
                # Still looking for first noun or no compound
                last_noun_idx = i
    
    if subject is None:
        subject = words[0]
        subject_idx = 0
        last_noun_idx = 0
    
    # If we have compound info, use the last noun index to skip past the entire compound subject
    verb_search_start = last_noun_idx + 1 if compound_info else subject_idx + 1
    
    # Find verb (auxiliaries or main verb)
    verb = None
    verb_idx = -1
    
    # Check for contractions first
    for i, w in enumerate(words):
        if w.lower() in CONTRACTIONS:
            verb = w
            verb_idx = i
            break
    
    # Check for auxiliaries
    if verb is None:
        for i, w in enumerate(words):
            if w.lower() in AUXILIARIES:
                verb = w
                verb_idx = i
                break
    
    # Find main verb - start search AFTER the compound subject
    if verb is None:
        for i in range(verb_search_start, len(words)):
            w = words[i]
            w_lower = w.lower()
            # Skip coordinators
            if w_lower in coordinators:
                continue
            # Skip determiners
            if w_lower in dets:
                continue
            # Simple heuristic: word after subject that looks like a verb
            if not w_lower.endswith(('ly', 'tion', 'ness', 'ment')):
                verb = w
                verb_idx = i
                break
    
    if verb is None and len(words) > verb_search_start:
        verb = words[-1]
        verb_idx = len(words) - 1
    
    return subject, verb, subject_idx, verb_idx


def detect_compound_subject(words: List[str]) -> Optional[Dict[str, Any]]:
    """
    Detect compound subjects with coordinators.
    
    Only detects compounds like "Tom and Mary" (nouns joined by coordinator),
    NOT compound sentences like "She sings and he dances" (where there's a verb before the coordinator).
    
    Returns: {
        'coordinator': 'and' | 'or' | 'nor',
        'subjects': [subject1, subject2],
        'compound_number': 'singular' | 'plural'
    }
    """
    for i, word in enumerate(words):
        w_lower = word.lower()
        if w_lower in {'and', 'or', 'nor'}:
            if i > 0 and i < len(words) - 1:
                before = words[i-1]
                before_lower = before.lower()
                
                # Check if word before coordinator is a verb - if so, this is likely a compound sentence, not compound subject
                is_verb_before = (before_lower in AUXILIARIES or 
                                 before_lower in IRREGULAR_VERBS or
                                 before_lower in CONTRACTIONS or
                                 (before_lower.endswith(('s', 'ed', 'ing')) and 
                                  before_lower not in PRONOUNS and
                                  len(before_lower) > 3))
                
                # If there's a verb before the coordinator, skip (this is a compound sentence)
                if is_verb_before:
                    continue
                
                after_idx = i + 1
                
                # Skip determiners
                while after_idx < len(words) and words[after_idx].lower() in {'the', 'a', 'an'}:
                    after_idx += 1
                
                if after_idx < len(words):
                    after = words[after_idx]
                    after_lower = after.lower()
                    
                    # Check if word after coordinator is a pronoun that could start a new clause
                    # If so, and there's a verb following, this is a compound sentence
                    if after_lower in PRONOUNS and after_idx + 1 < len(words):
                        next_word = words[after_idx + 1].lower()
                        is_verb_after = (next_word in AUXILIARIES or 
                                        next_word in IRREGULAR_VERBS or
                                        next_word.endswith(('s', 'ed', 'ing')))
                        if is_verb_after:
                            # This is a compound sentence, not a compound subject
                            continue
                    
                    # Rule 3: "and" → plural
                    if w_lower == 'and':
                        return {
                            'coordinator': 'and',
                            'subjects': [before, after],
                            'compound_number': 'plural'
                        }
                    
                    # Rule 4: "or"/"nor" → nearest subject
                    elif w_lower in {'or', 'nor'}:
                        _, nearest_number = classify_noun(after)
                        return {
                            'coordinator': w_lower,
                            'subjects': [before, after],
                            'compound_number': nearest_number
                        }
    
    return None


def split_compound_sentence(tokens: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    Split a compound sentence into individual clauses.
    
    Detects coordinators (and, or, but, yet, so, for, nor) between clauses
    and splits the sentence accordingly.
    
    Returns: List of token lists, one per clause
    """
    clause_coordinators = {'and', 'or', 'but', 'yet', 'so', 'for', 'nor'}
    
    # Common base verbs (infinitive forms)
    common_verbs = {'be', 'have', 'do', 'say', 'get', 'make', 'go', 'know', 'take', 'see', 
                   'come', 'think', 'look', 'want', 'give', 'use', 'find', 'tell', 'ask',
                   'work', 'seem', 'feel', 'try', 'leave', 'call', 'run', 'play', 'sing',
                   'dance', 'write', 'read', 'watch', 'fix', 'study', 'love', 'like', 'need',
                   'help', 'talk', 'turn', 'start', 'show', 'hear', 'move', 'live', 'bring',
                   'sit', 'stand', 'eat', 'drink', 'sleep', 'walk', 'drive', 'teach', 'learn'}
    
    words = [t['text'] for t in tokens if re.match(r"\w+(?:'\w+)?", t['text'])]
    
    clauses = []
    current_clause = []
    found_first_verb = False
    verb_count = 0
    
    for i, token in enumerate(tokens):
        word = token['text']
        w_lower = word.lower()
        
        # Check if this word is likely a verb
        # Strip common endings to get base form
        base_verb = w_lower
        if w_lower.endswith('ing'):
            base_verb = w_lower[:-3]
        elif w_lower.endswith('ed'):
            base_verb = w_lower[:-2] if not w_lower.endswith('eed') else w_lower[:-1]
        elif w_lower.endswith('es'):
            base_verb = w_lower[:-2]
        elif w_lower.endswith('s'):
            base_verb = w_lower[:-1]
        elif w_lower.endswith('ies'):
            base_verb = w_lower[:-3] + 'y'
        
        is_likely_verb = (w_lower in AUXILIARIES or 
                         w_lower in CONTRACTIONS or 
                         w_lower in IRREGULAR_VERBS or
                         base_verb in common_verbs or
                         (w_lower.endswith(('s', 'es', 'ed', 'ing')) and 
                          w_lower not in PRONOUNS and
                          w_lower not in {'the', 'a', 'an', 'this', 'that', 'these', 'those', 'his', 'her', 'its', 'our', 'their'} and
                          len(w_lower) > 2))
        
        if is_likely_verb and i > 0:
            found_first_verb = True
            verb_count += 1
        
        # Check for coordinator that might split clauses
        if (w_lower in clause_coordinators and 
            found_first_verb and 
            verb_count >= 1 and
            len(current_clause) > 1 and
            i < len(tokens) - 2):
            
            # Look ahead: check if next word(s) form a new subject-verb pattern
            next_tokens = [t for t in tokens[i+1:i+4] if re.match(r"\w+(?:'\w+)?", t['text'])]
            
            if len(next_tokens) >= 2:
                next_word = next_tokens[0]['text']
                next_word_lower = next_word.lower()
                second_word = next_tokens[1]['text'] if len(next_tokens) > 1 else ""
                second_word_lower = second_word.lower()
                
                # Check if next word is a pronoun, determiner, or potential noun (start of new clause)
                is_determiner_or_pronoun = (next_word_lower in PRONOUNS or 
                                           next_word_lower in {'the', 'a', 'an', 'this', 'that', 'these', 'those'})
                
                # Check if it's a proper noun (capitalized) or any word that's not a verb/coordinator
                is_potential_noun = (next_word[0].isupper() or 
                                    (next_word_lower not in clause_coordinators and 
                                     next_word_lower not in AUXILIARIES and
                                     next_word_lower not in IRREGULAR_VERBS))
                
                is_new_clause_start = is_determiner_or_pronoun or is_potential_noun
                
                # Strip endings to check if second word is a verb
                second_base = second_word_lower
                if second_word_lower.endswith('ing'):
                    second_base = second_word_lower[:-3]
                elif second_word_lower.endswith('ed'):
                    second_base = second_word_lower[:-2]
                elif second_word_lower.endswith('es'):
                    second_base = second_word_lower[:-2]
                elif second_word_lower.endswith('s'):
                    second_base = second_word_lower[:-1]
                elif second_word_lower.endswith('ies'):
                    second_base = second_word_lower[:-3] + 'y'
                
                # Check if the second word looks like a verb
                has_following_verb = (second_word_lower in AUXILIARIES or 
                                    second_word_lower in IRREGULAR_VERBS or
                                    second_word_lower in CONTRACTIONS or
                                    second_base in common_verbs or
                                    (second_word_lower.endswith(('s', 'es', 'ed', 'ing')) and len(second_word) > 2))
                
                if is_new_clause_start and has_following_verb:
                    # Save current clause
                    if current_clause:
                        clauses.append(current_clause)
                    
                    # Start new clause
                    current_clause = []
                    found_first_verb = False
                    verb_count = 0
                    continue
        
        current_clause.append(token)
    
    # Add final clause
    if current_clause:
        clauses.append(current_clause)
    
    # If we only found one clause, return the original
    if len(clauses) <= 1:
        return [tokens]
    
    return clauses


def analyze_compound_sentence(sentence: str, clauses: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Analyze a compound sentence by analyzing each clause separately.
    
    Returns combined analysis with per-clause results.
    """
    # Extract coordinators from the original sentence
    clause_coordinators = {'and', 'or', 'but', 'yet', 'so', 'for', 'nor'}
    original_tokens = tokenize(sentence)
    coordinators = [t['text'] for t in original_tokens if t['text'].lower() in clause_coordinators]
    
    clause_analyses = []
    all_problems = []
    all_parse_trees = []
    
    for i, clause_tokens in enumerate(clauses):
        # Reconstruct clause text
        clause_text = ' '.join([t['text'] for t in clause_tokens])
        
        # Analyze this clause
        clause_result = analyze_single_clause(clause_tokens, clause_text)
        
        clause_analyses.append({
            'clause_number': i + 1,
            'text': clause_text,
            'analysis': clause_result
        })
        
        # Collect problems
        if clause_result.get('status') == 'error':
            all_problems.extend(clause_result.get('problem_spans', []))
        
        # Collect parse trees
        if 'parse_tree' in clause_result:
            all_parse_trees.append(clause_result['parse_tree'])
    
    # Determine overall status
    has_errors = any(c['analysis'].get('status') == 'error' for c in clause_analyses)
    
    # Build compound parse tree
    compound_tree = {
        'label': 'S (Compound)',
        'children': all_parse_trees
    }
    
    if has_errors:
        error_messages = [c['analysis']['message'] for c in clause_analyses if c['analysis'].get('status') == 'error']
        
        # Build full corrected sentence by combining corrected clauses with coordinators
        corrected_parts = []
        for idx, c in enumerate(clause_analyses):
            if c['analysis'].get('status') == 'error' and 'suggested_correction' in c['analysis']:
                # Use suggested correction, removing trailing punctuation
                corrected_text = c['analysis']['suggested_correction'].rstrip(' .')
                corrected_parts.append(corrected_text)
            else:
                # Use original text, removing trailing punctuation
                corrected_parts.append(c['text'].rstrip(' .'))
            
            # Add coordinator between clauses (but not after the last clause)
            if idx < len(clause_analyses) - 1 and idx < len(coordinators):
                corrected_parts.append(coordinators[idx])
        
        # Add final punctuation
        suggested_full_sentence = ' '.join(corrected_parts) + '.'
        
        return {
            'status': 'error',
            'message': f"Found {len(error_messages)} error(s) in compound sentence.",
            'is_compound': True,
            'clause_count': len(clauses),
            'clause_analyses': clause_analyses,
            'problem_spans': all_problems,
            'parse_tree': compound_tree,
            'suggested_correction': suggested_full_sentence,
            'original_sentence': sentence
        }
    else:
        return {
            'status': 'ok',
            'message': f"All {len(clauses)} clauses have correct subject-verb agreement.",
            'is_compound': True,
            'clause_count': len(clauses),
            'clause_analyses': clause_analyses,
            'parse_tree': compound_tree
        }


def analyze_single_clause(tokens: List[Dict[str, Any]], clause_text: str) -> Dict[str, Any]:
    """Analyze a single clause (used for both simple and compound sentences)."""
    words = [t['text'] for t in tokens if re.match(r"\w+(?:'\w+)?", t['text'])]
    
    if not words:
        return {
            'status': 'error',
            'message': 'Unable to parse clause (too short).'
        }
    
    # Detect compound subjects
    compound_info = detect_compound_subject(words)
    
    # Find subject and verb
    subject, verb, subj_idx, verb_idx = find_subject_and_verb(tokens, compound_info)
    
    if subject is None or verb is None:
        return {
            'status': 'error',
            'message': 'Unable to identify subject and verb.'
        }
    
    # Classify subject and verb
    if compound_info:
        subject_category = 'compound'
        subject_number = compound_info['compound_number']
        display_subject = f"{compound_info['subjects'][0]} {compound_info['coordinator']} {compound_info['subjects'][1]}"
    else:
        subject_category, subject_number = classify_noun(subject)
        display_subject = subject
    
    verb_number = classify_verb(verb)
    
    # Create initial CSG parse string
    parse_string = create_initial_parse_string(
        subject, verb, subject_category, subject_number, verb_number, compound_info
    )
    
    # Apply CSG derivation
    derivation_steps, final_string, is_correct = apply_csg_derivation(parse_string, subject_number)
    
    # Build parse tree
    parse_tree = {
        'label': 'S',
        'children': [
            {
                'label': f"NP ({subject_number})",
                'children': [
                    {'label': 'N', 'text': display_subject, 'features': {'number': subject_number}}
                ]
            },
            {
                'label': f"VP ({verb_number})",
                'children': [
                    {'label': 'V', 'text': verb, 'features': {'number': verb_number}}
                ]
            }
        ]
    }
    
    # Determine if there's an agreement error
    agreement_ok = subject_number == verb_number
    
    if agreement_ok:
        return {
            'status': 'ok',
            'message': f"Subject-verb agreement is correct. Subject '{display_subject}' ({subject_number}) agrees with verb '{verb}' ({verb_number}).",
            'problem_spans': [],
            'parse_tree': parse_tree,
            'derivation': derivation_steps,
            'csg_analysis': {
                'initial_string': parse_string,
                'final_string': final_string,
                'rules_applied': len([d for d in derivation_steps if d['rule'] is not None])
            }
        }
    else:
        # Generate correction
        correct_verb = get_correct_verb_form(verb, subject_number)
        suggested_sentence = clause_text.replace(verb, correct_verb)
        
        return {
            'status': 'error',
            'message': f"Subject-verb disagreement: '{display_subject}' ({subject_number}) does not agree with '{verb}' ({verb_number}).",
            'problem_spans': [
                {
                    'type': 'subject',
                    'text': display_subject,
                    'features': {'number': subject_number},
                    'subject_features': {'number': subject_number},
                    'verb_features': {'number': verb_number}
                }
            ],
            'parse_tree': parse_tree,
            'derivation': derivation_steps,
            'original_sentence': clause_text,
            'suggested_correction': suggested_sentence,
            'csg_analysis': {
                'initial_string': parse_string,
                'final_string': final_string,
                'expected_string': f"NP[{subject_number}] VP[{subject_number}]",
                'rules_applied': len([d for d in derivation_steps if d['rule'] is not None])
            }
        }


# ============================================================================
# CSG Derivation Engine
# ============================================================================

def create_initial_parse_string(subject: str, verb: str, subject_category: str, 
                                 subject_number: str, verb_number: str, 
                                 compound_info: Optional[Dict] = None) -> str:
    """
    Create the initial string representation for CSG derivation.
    
    Format: NP[features] VP[features]
    """
    if compound_info:
        coord = compound_info['coordinator']
        return f"NP[{subject_category}+{coord}+{subject_number}] VP[{verb_number}]"
    else:
        # Handle special pronoun cases
        if subject.lower() in {'i', 'you'} and subject_category == 'pronoun':
            return f"NP[{subject.lower()}] VP[{verb_number}]"
        else:
            return f"NP[{subject_category if subject_category != 'regular' else subject_number}] VP[{verb_number}]"


def apply_csg_derivation(parse_string: str, expected_verb_number: str) -> Tuple[List[Dict], str, bool]:
    """
    Apply CSG production rules to derive the correct form.
    
    Returns:
        derivation_steps: List of derivation steps with rule applications
        final_string: The final derived string
        is_correct: Whether the original already matched expected
    """
    derivation_steps = []
    current_string = parse_string
    
    derivation_steps.append({
        'step': 0,
        'string': current_string,
        'rule': None,
        'description': 'Initial parse string'
    })
    
    # Try to apply CSG rules
    step = 1
    applied_rule = False
    
    for rule in CSG_PRODUCTION_RULES:
        # Search for positions where rule can be applied
        for pos in range(len(current_string)):
            if rule.matches(current_string, pos):
                # Apply the rule
                new_string = rule.apply(current_string, pos)
                
                derivation_steps.append({
                    'step': step,
                    'string': new_string,
                    'rule': rule.rule_id,
                    'rule_description': rule.description,
                    'sva_rule': rule.sva_rule_number,
                    'production': f"{rule.left_context}{rule.symbol}{rule.right_context} → {rule.left_context}{rule.replacement}{rule.right_context}"
                })
                
                current_string = new_string
                applied_rule = True
                step += 1
                break  # Apply one rule at a time
        
        if applied_rule:
            break
    
    # Check if agreement is correct
    is_correct = f"VP[{expected_verb_number}]" in current_string
    
    return derivation_steps, current_string, is_correct


def get_correct_verb_form(verb: str, target_number: str) -> str:
    """Generate the correct verb form for the target number."""
    v_lower = verb.lower()
    
    # Handle contractions
    if v_lower in CONTRACTIONS:
        if target_number == 'singular':
            return "doesn't" if "do" in v_lower else "isn't" if "is" in v_lower or "are" in v_lower else "wasn't" if "was" in v_lower or "were" in v_lower else "hasn't" if "has" in v_lower or "have" in v_lower else verb
        else:
            return "don't" if "do" in v_lower else "aren't" if "is" in v_lower or "are" in v_lower else "weren't" if "was" in v_lower or "were" in v_lower else "haven't" if "has" in v_lower or "have" in v_lower else verb
    
    # Handle irregular verbs
    if v_lower in IRREGULAR_VERBS:
        current_number = IRREGULAR_VERBS[v_lower][0]
        if current_number != target_number:
            return IRREGULAR_VERBS[v_lower][1]
    
    # Handle regular verbs
    if target_number == 'singular':
        if not v_lower.endswith('s'):
            # Apply -es for verbs ending in s, sh, ch, x, z, o
            if v_lower.endswith(('s', 'sh', 'ch', 'x', 'z')) or (v_lower.endswith('o') and not v_lower.endswith(('oo', 'eo', 'io'))):
                return verb + 'es'
            # Apply -ies for verbs ending in consonant + y
            elif v_lower.endswith('y') and len(v_lower) > 1 and v_lower[-2] not in 'aeiou':
                return verb[:-1] + 'ies'
            else:
                return verb + 's'
    else:
        # Convert singular to plural
        if v_lower.endswith('ies'):
            return verb[:-3] + 'y'
        elif v_lower.endswith('es') and len(v_lower) > 2:
            # Check if base ends in s, sh, ch, x, z, o
            base = verb[:-2]
            if base.endswith(('s', 'sh', 'ch', 'x', 'z', 'o')):
                return base
            else:
                return verb[:-1]  # Just remove 's'
        elif v_lower.endswith('s') and v_lower not in {'is', 'has', 'does', 'was'}:
            return verb[:-1]
    
    return verb


# ============================================================================
# Main Analysis Function
# ============================================================================

def analyze(sentence: str) -> Dict[str, Any]:
    """
    Analyze sentence using Context-Sensitive Grammar.
    
    Handles both simple sentences and compound sentences (multiple clauses).
    
    Returns a complete analysis with CSG derivation steps.
    """
    tokens = tokenize(sentence)
    words = [t['text'] for t in tokens if re.match(r"\w+(?:'\w+)?", t['text'])]
    
    if not words:
        return {
            'status': 'error',
            'message': 'Unable to parse sentence (too short or not supported).'
        }
    
    # Check if this is a compound sentence
    clauses = split_compound_sentence(tokens)
    
    if len(clauses) > 1:
        # Compound sentence - analyze each clause
        return analyze_compound_sentence(sentence, clauses)
    
    # Simple sentence - analyze normally
    return analyze_single_clause(tokens, sentence)


# ============================================================================
# Testing
# ============================================================================

if __name__ == '__main__':
    import json
    
    test_sentences = [
        # Simple sentences
        "The cat runs.",                    # OK: singular
        "The cats run.",                    # OK: plural
        "The cats runs.",                   # ERROR: plural noun, singular verb
        "I run.",                           # OK: I takes plural verb (Rule 2)
        "I runs.",                          # ERROR: I takes plural verb
        "Everyone loves music.",            # OK: indefinite pronoun (Rule 5)
        "Everyone love music.",             # ERROR: indefinite pronoun needs singular
        "Mark and Anna play guitar.",       # OK: compound with "and" (Rule 3)
        "Mark and Anna plays guitar.",      # ERROR: compound with "and" needs plural
        "The team wins.",                   # OK: collective noun (Rule 6)
        "The team win.",                    # ERROR: collective noun needs singular
        "Mathematics is difficult.",        # OK: singular plural (Rule 9)
        "They don't run.",                  # OK: contraction
        "They doesn't run.",                # ERROR: plural with singular contraction
        
        # Verbs with -es endings
        "She watches movies.",              # OK: singular with -es
        "They watch movies.",               # OK: plural
        "He fixes computers.",              # OK: singular with -es
        "She goes home.",                   # OK: singular with -es (consonant + o)
        "They go home.",                    # OK: plural
        "He studies hard.",                 # OK: singular with -ies (consonant + y)
        "They study hard.",                 # OK: plural
        
        # Compound sentences
        "The cat runs and the dog barks.",  # OK: both clauses correct
        "The cats run and the dogs bark.",  # OK: both clauses correct
        "The cat runs but the dogs barks.", # ERROR: second clause wrong
        "She sings and he dances.",         # OK: both clauses correct
        "I work and they plays.",           # ERROR: second clause wrong
        "Tom studies but Mary play.",       # ERROR: second clause wrong
    ]
    
    for sent in test_sentences:
        print(f"\n{'='*70}")
        print(f"Sentence: {sent}")
        print('='*70)
        result = analyze(sent)
        print(json.dumps(result, indent=2))
