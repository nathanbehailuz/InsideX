import React from 'react';
import './HowItWorks.css';

const HowItWorks = () => {
  const steps = [
    {
      id: 'etl',
      title: 'ETL',
      description: 'Extract, Transform, Load SEC Form 4 filings data'
    },
    {
      id: 'score',
      title: 'Score',
      description: 'Apply proprietary algorithms to evaluate trade significance'
    },
    {
      id: 'signal',
      title: 'Signal',
      description: 'Generate deterministic alerts for high-impact trades'
    },
    {
      id: 'track',
      title: 'Track',
      description: 'Monitor performance and refine scoring models'
    }
  ];

  return (
    <section className="how-it-works">
      <div className="container">
        <h2 className="section-title">How it works</h2>
        <div className="steps-container">
          {steps.map((step, index) => (
            <div key={step.id} className="step">
              <div className="step-number">{index + 1}</div>
              <h3 className="step-title">{step.title}</h3>
              <p className="step-description">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks; 