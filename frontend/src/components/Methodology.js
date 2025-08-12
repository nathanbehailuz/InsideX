import React from 'react';
import './Methodology.css';

const Methodology = () => {
  const methodologyPoints = [
    'SEC Form 4 filings are public records with standardized reporting requirements',
    'Proprietary scoring algorithm considers trade size, executive role, and company context',
    'Bias controls include random sampling validation and cross-company comparisons',
    'Continuous model refinement based on market performance feedback',
    'Transparent methodology with regular audit reviews'
  ];

  return (
    <section className="methodology">
      <div className="container">
        <h2 className="section-title">Methodology & bias controls</h2>
        <div className="methodology-content">
          <p className="methodology-intro">
            Our approach combines regulatory compliance with advanced analytics to deliver 
            reliable, actionable insights from executive trading activity.
          </p>
          <div className="methodology-points">
            {methodologyPoints.map((point, index) => (
              <div key={index} className="methodology-point">
                <div className="point-icon">✓</div>
                <p className="point-text">{point}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Methodology; 