# Extended grammar engine - features to add to engine.py

# Enhanced tokenization regex
TOKENIZE_PATTERN = r"\w+(?:'\w+)?|[^\s\w]"  # Handles contractions like don't, isn't

# Pronoun lookup table
# Note: "I" and "you" take plural verb forms (e.g., "I run", "you run", not "I runs")
# Exception: "I am" is the only singular form for "I"
PRONOUNS = {
    'i': {'number': 'plural', 'person': 1},      # Takes plural verbs: "I run", "I play"
    'you': {'number': 'plural', 'person': 2},    # Takes plural verbs: "you run", "you play"
    'he': {'number': 'singular', 'person': 3},
    'she': {'number': 'singular', 'person': 3},
    'it': {'number': 'singular', 'person': 3},
    'we': {'number': 'plural', 'person': 1},
    'they': {'number': 'plural', 'person': 3},
}

# Irregular verbs
IRREGULAR_VERBS = {
    'is': ('singular', 'are'),
    'are': ('plural', 'is'),
    'was': ('singular', 'were'),
    'were': ('plural', 'was'),
    'has': ('singular', 'have'),
    'have': ('plural', 'has'),
    'does': ('singular', 'do'),
    'do': ('plural', 'does'),
}

# Contractions (with and without apostrophes for flexibility)
CONTRACTIONS = {
    "don't": 'plural',
    "dont": 'plural',  # Without apostrophe
    "doesn't": 'singular',
    "doesnt": 'singular',  # Without apostrophe
    "isn't": 'singular',
    "isnt": 'singular',  # Without apostrophe
    "aren't": 'plural',
    "arent": 'plural',  # Without apostrophe
    "wasn't": 'singular',
    "wasnt": 'singular',  # Without apostrophe
    "weren't": 'plural',
    "werent": 'plural',  # Without apostrophe
    "haven't": 'plural',
    "havent": 'plural',  # Without apostrophe
    "hasn't": 'singular',
    "hasnt": 'singular',  # Without apostrophe
    "won't": 'singular',  # will not
    "wont": 'singular',
    "can't": 'plural',  # can not
    "cant": 'plural',
}

# Auxiliaries
AUXILIARIES = {'is', 'are', 'was', 'were', 'has', 'have', 'do', 'does', 'will', 'can', 'should', 'would', 'could'}

# Coordinators
COORDINATORS = {'and', 'or', 'nor'}

# Rule 5: Indefinite pronouns (always singular)
INDEFINITE_PRONOUNS = {
    'everyone', 'everybody', 'everything',
    'someone', 'somebody', 'something',
    'anyone', 'anybody', 'anything',
    'no one', 'nobody', 'nothing',
    'each', 'either', 'neither',
    'one', 'another', 'other'
}

# Rule 6: Collective nouns (usually singular - treated as one unit)
COLLECTIVE_NOUNS = {
    'team', 'group', 'class', 'family', 'committee', 'staff',
    'crew', 'audience', 'band', 'jury', 'council', 'crowd',
    'company', 'government', 'organization', 'department',
    'army', 'navy', 'police', 'public'
}

# Rule 8: Units that are treated as singular (amount, time, money, distance)
UNIT_WORDS = {'dollars', 'pesos', 'pounds', 'euros', 'cents',
              'hours', 'minutes', 'seconds', 'days', 'weeks', 'months', 'years',
              'miles', 'kilometers', 'meters', 'feet',
              'kilograms', 'pounds', 'ounces'}

# Rule 9: Countries and subjects that look plural but are singular
SINGULAR_PLURALS = {
    'philippines', 'united states', 'netherlands',
    'mathematics', 'physics', 'economics', 'politics',
    'news', 'measles', 'mumps', 'diabetes',
    'athletics', 'gymnastics', 'statistics'
}
