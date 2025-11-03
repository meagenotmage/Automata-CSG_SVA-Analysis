from flask import Flask, request, jsonify
import os
import json
from importlib import util as importlib_util

app = Flask(__name__)


def load_engine_module():
    # Load grammar_engine/engine.py dynamically so the backend can call analyze()
    engine_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'grammar_engine', 'engine.py'))
    if not os.path.exists(engine_path):
        return None
    spec = importlib_util.spec_from_file_location('grammar_engine.engine', engine_path)
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

    engine = load_engine_module()
    if engine is None:
        return jsonify({'status': 'error', 'message': 'Grammar engine not found.'}), 500

    # Call the grammar engine's analyze function
    result = engine.analyze(sentence)
    return jsonify(result)


if __name__ == '__main__':
    # default port 5000, bound to localhost
    app.run(host='127.0.0.1', port=5000, debug=True)
