import React from 'react';
import './App.css';
import Hero from './components/Hero';
import HowItWorks from './components/HowItWorks';
import WhatYouReceive from './components/WhatYouReceive';
import Methodology from './components/Methodology';
import Disclaimer from './components/Disclaimer';

function App() {
  return (
    <div className="App">
      <Hero />
      <HowItWorks />
      <WhatYouReceive />
      <Methodology />
      <Disclaimer />
    </div>
  );
}

export default App;
