import React from 'react';
import './DerivationSteps.css';

const DerivationSteps = ({ steps }) => {
  return (
    <div className="derivation-steps">
      {steps.map((step, idx) => (
        <div key={idx} className="derivation-step">
          <div className="step-number">{step.step}</div>
          <div className="step-content">
            <div className="step-rule">{step.rule}</div>
            <div className="step-description">{step.description}</div>
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
