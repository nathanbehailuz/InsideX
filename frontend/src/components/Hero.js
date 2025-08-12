import React from 'react';
import './Hero.css';

const Hero = () => {
  const handleSignUp = () => {
    // TODO: Implement auth flow
    console.log('Sign up clicked');
  };

  return (
    <section className="hero">
      <div className="hero-container">
        <h1 className="hero-title">
          Insidex — Executive trades, indexed.
        </h1>
        <p className="hero-subtitle">
          Scan. Score. Signal. Deterministic alerts from SEC Form 4 filings.
        </p>
        <button className="hero-cta" onClick={handleSignUp}>
          Sign up for alerts
        </button>
      </div>
    </section>
  );
};

export default Hero; 