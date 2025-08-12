import React from 'react';
import './WhatYouReceive.css';

const WhatYouReceive = () => {
  const sampleAlerts = [
    'Real-time notifications for executive trades above $100K',
    'Scored significance ratings (1-10) for each trade',
    'Company context and executive background information',
    'Historical trading patterns and trend analysis',
    'Customizable alert thresholds and preferences'
  ];

  return (
    <section className="what-you-receive">
      <div className="container">
        <h2 className="section-title">What you'll receive</h2>
        <div className="alerts-container">
          {sampleAlerts.map((alert, index) => (
            <div key={index} className="alert-item">
              <div className="alert-bullet">•</div>
              <p className="alert-text">{alert}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default WhatYouReceive; 