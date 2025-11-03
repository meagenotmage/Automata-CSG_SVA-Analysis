import React, { useState } from 'react';
import axios from 'axios';
import ParseTreeVisualizer from './components/ParseTreeVisualizer';
import DerivationSteps from './components/DerivationSteps';
import './App.css';

function App() {
  const [sentence, setSentence] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [engine, setEngine] = useState('csg'); // 'csg' or 'rule'

  const handleAnalyze = async () => {
    if (!sentence.trim()) {
      setError('Please enter a sentence');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/parse', {
        sentence: sentence,
        engine: engine
      });
      setResult(response.data);
    } catch (err) {
      setError('Failed to analyze sentence. Make sure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAnalyze();
    }
  };

  const exampleSentences = [
    'The cats runs.',
    'The cat and the dog runs.',
    "They don't run.",
    'He runs fast.',
    'The children plays.',
  ];

  return (
    <div className="App">
      <header className="App-header">
        <h1>Subject–Verb Agreement</h1>
        <p className="subtitle">
          {engine === 'csg' ? 'Context-Sensitive Grammar (Automata Theory)' : 'Rule-Based Analysis'}
        </p>
      </header>

      <main className="main-content">
        <div className="input-section">
          {/* Engine Selector */}
          <div className="engine-selector">
            <label className="engine-label">Grammar Engine:</label>
            <div className="engine-options">
              <button 
                className={`engine-option ${engine === 'csg' ? 'active' : ''}`}
                onClick={() => setEngine('csg')}
              >
                <span className="engine-name">CSG Engine</span>
                <span className="engine-desc">Context-Sensitive Grammar</span>
              </button>
              <button 
                className={`engine-option ${engine === 'rule' ? 'active' : ''}`}
                onClick={() => setEngine('rule')}
              >
                <span className="engine-name">Rule-Based</span>
                <span className="engine-desc">Pattern matching with heuristics</span>
              </button>
            </div>
          </div>

          <div className="input-container">
            <textarea
              className="sentence-input"
              value={sentence}
              onChange={(e) => setSentence(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter a sentence to analyze (e.g., 'The cats runs.')"
              rows="3"
            />
            <button 
              className="analyze-button" 
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>

          <div className="examples">
            <p className="examples-label">Try these examples:</p>
            <div className="example-buttons">
              {exampleSentences.map((ex, idx) => (
                <button
                  key={idx}
                  className="example-button"
                  onClick={() => setSentence(ex)}
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}
        </div>

        {result && (
          <div className="results-section">
            {/* Primary Result: Error/Success Message */}
            <div className="status-card">
              <div className={`status-badge ${result.status}`}>
                {result.status === 'ok' ? '✓ Correct Agreement' : '✗ Agreement Error'}
              </div>
              <p className="status-message">{result.message}</p>
              
              {/* Show suggested correction prominently if there's an error */}
              {result.status === 'error' && (
                <div className="correction-suggestion">
                  <strong>Suggested Correction:</strong>
                  {result.suggested_correction ? (
                    <div className="corrected-sentence">
                      "{result.suggested_correction}"
                    </div>
                  ) : result.problem_spans && result.problem_spans.length > 0 ? (
                    <p>
                      {result.problem_spans.map((span, idx) => (
                        <span key={idx}>
                          {span.subject_features && span.verb_features && (
                            <>
                              The subject is <span className="highlight-subject">{span.subject_features.number}</span>,
                              {' '}but the verb is <span className="highlight-verb">{span.verb_features.number}</span>.
                              {' '}Use a {span.subject_features.number} verb instead.
                            </>
                          )}
                        </span>
                      ))}
                    </p>
                  ) : null}
                </div>
              )}
            </div>

            {/* Optional Details: Problem Spans */}
            {result.problem_spans && result.problem_spans.length > 0 && (
              <details className="details-section">
                <summary>View Problem Spans</summary>
                <div className="problem-spans">
                  <div className="spans-list">
                    {result.problem_spans.map((span, idx) => (
                      <div key={idx} className="span-item">
                        <span className="span-type">{span.type}</span>
                        <span className="span-text">"{span.text}"</span>
                        <span className="span-features">
                          {span.features.number}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </details>
            )}

            {/* Optional Details: Parse Tree */}
            {result.parse_tree && (
              <details className="details-section">
                <summary>View Parse Tree</summary>
                <div className="parse-tree-section">
                  <ParseTreeVisualizer tree={result.parse_tree} />
                </div>
              </details>
            )}

            {/* CSG Analysis Info */}
            {result.csg_analysis && (
              <details className="details-section csg-section" open>
                <summary>CSG Derivation Analysis</summary>
                <div className="csg-analysis">
                  <div className="csg-info-grid">
                    <div className="csg-info-item">
                      <strong>Initial String:</strong>
                      <code>{result.csg_analysis.initial_string}</code>
                    </div>
                    <div className="csg-info-item">
                      <strong>Final String:</strong>
                      <code>{result.csg_analysis.final_string}</code>
                    </div>
                    {result.csg_analysis.expected_string && (
                      <div className="csg-info-item">
                        <strong>Expected String:</strong>
                        <code>{result.csg_analysis.expected_string}</code>
                      </div>
                    )}
                    <div className="csg-info-item">
                      <strong>Rules Applied:</strong>
                      <span className="rule-count">{result.csg_analysis.rules_applied}</span>
                    </div>
                  </div>
                </div>
              </details>
            )}

            {/* Optional Details: Derivation Steps */}
            {result.derivation && result.derivation.length > 0 && (
              <details className="details-section" open={result.engine_used === 'csg'}>
                <summary>
                  {result.engine_used === 'csg' ? 'CSG Production Rules Applied' : 'View Derivation Steps'}
                </summary>
                <div className="derivation-section">
                  <DerivationSteps steps={result.derivation} />
                </div>
              </details>
            )}
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>
          {engine === 'csg' 
            ? 'Using Context-Sensitive Grammar from Automata Theory' 
            : 'Using Rule-Based Pattern Matching'}
          {' • Flask + React + D3'}
        </p>
      </footer>
    </div>
  );
}

export default App;
