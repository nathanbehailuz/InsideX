import React from 'react';
import './Disclaimer.css';

const Disclaimer = () => {
  return (
    <div className="disclaimer-banner">
      <div className="disclaimer-content">
        <p className="disclaimer-text">
          <strong>Disclaimer:</strong> This information is for educational purposes only and does not constitute 
          investment advice. Past performance does not guarantee future results. Always conduct your own research 
          and consult with qualified financial professionals before making investment decisions.
        </p>
      </div>
    </div>
  );
};

export default Disclaimer; 