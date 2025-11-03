import json
from grammar_engine import engine


def test_sva_mismatch():
    res = engine.analyze('The cats runs.')
    assert res['status'] == 'error'
    assert 'cats' in res['message']
    assert 'runs' in res['message']


def test_sva_ok_singular():
    res = engine.analyze('The cat runs.')
    assert res['status'] == 'ok'


def test_sva_ok_plural():
    res = engine.analyze('The cats run.')
    assert res['status'] == 'ok'


def test_contraction_plural_correct():
    """Test that 'They don't run' is correctly identified as valid."""
    res = engine.analyze("They don't run.")
    assert res['status'] == 'ok'


def test_contraction_singular_correct():
    """Test that 'He doesn't run' is correctly identified as valid."""
    res = engine.analyze("He doesn't run.")
    assert res['status'] == 'ok'


def test_contraction_mismatch():
    """Test that 'They doesn't run' is correctly identified as an error."""
    res = engine.analyze("They doesn't run.")
    assert res['status'] == 'error'
    assert 'They' in res['message']
    assert "doesn't" in res['message']


if __name__ == '__main__':
    print(json.dumps(engine.analyze('The cats runs.'), indent=2))
