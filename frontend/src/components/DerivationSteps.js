import React from 'react';
import './DerivationSteps.css';

const DerivationSteps = ({ steps }) => {
  return (
    <div className="derivation-steps">
      {steps.map((step, idx) => (
        <div key={idx} className={`derivation-step ${step.rule ? 'has-rule' : 'initial'}`}>
          <div className="step-header">
            <div className="step-number">Step {step.step}</div>
            {step.sva_rule && (
              <div className="sva-rule-badge">SVA Rule #{step.sva_rule}</div>
            )}
          </div>
          
          <div className="step-content">
            {step.rule ? (
              <>
                <div className="step-rule">
                  <span className="rule-label">Rule:</span>
                  <code className="rule-id">{step.rule}</code>
                </div>
                
                {step.production && (
                  <div className="step-production">
                    <span className="production-label">Production:</span>
                    <code className="production-text">{step.production}</code>
                  </div>
                )}
                
                {step.rule_description && (
                  <div className="step-description">
                    <span className="desc-icon">ℹ️</span>
                    {step.rule_description}
                  </div>
                )}
                
                <div className="step-string">
                  <span className="string-label">Result:</span>
                  <code className="string-text">{step.string}</code>
                </div>
              </>
            ) : (
              <>
                <div className="step-description initial-desc">
                  {step.description}
                </div>
                <div className="step-string">
                  <code className="string-text">{step.string}</code>
                </div>
              </>
            )}
            
            {step.result && (
              <div className="step-result">
                <code>{typeof step.result === 'string' ? step.result : JSON.stringify(step.result)}</code>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default DerivationSteps;
