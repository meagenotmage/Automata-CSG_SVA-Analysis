from flask import Flask, request, jsonify
import os
import json
from importlib import util as importlib_util

app = Flask(__name__)


def load_engine_module(engine_type='csg'):
    """
    Load grammar engine module dynamically.
    
    Args:
        engine_type: 'csg' for Context-Sensitive Grammar engine (default),
                     'rule' for rule-based engine
    """
    if engine_type == 'csg':
        engine_filename = 'csg_engine.py'
    else:
        engine_filename = 'engine.py'
    
    engine_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'grammar_engine', engine_filename))
    if not os.path.exists(engine_path):
        return None
    spec = importlib_util.spec_from_file_location(f'grammar_engine.{engine_type}_engine', engine_path)
    module = importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'sva-visualizer-backend'})


@app.route('/parse', methods=['POST'])
def parse():
    data = request.get_json(silent=True) or {}
    sentence = data.get('sentence', '')
    engine_type = data.get('engine', 'csg')  # Default to CSG engine
    
    # Validate engine type
    if engine_type not in ['csg', 'rule']:
        return jsonify({'status': 'error', 'message': f'Invalid engine type: {engine_type}. Use "csg" or "rule".'}), 400

    engine = load_engine_module(engine_type)
    if engine is None:
        return jsonify({'status': 'error', 'message': f'Grammar engine "{engine_type}" not found.'}), 500

    # Call the grammar engine's analyze function
    result = engine.analyze(sentence)
    result['engine_used'] = engine_type  # Add metadata about which engine was used
    return jsonify(result)


if __name__ == '__main__':
    # default port 5000, bound to localhost
    app.run(host='127.0.0.1', port=5000, debug=True)
