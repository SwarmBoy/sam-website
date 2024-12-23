import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './Components/Home/Home';
import Circle from './Components/Circle/Circle';
import Experiment from './Components/Experiment/Experiment';
import Relative from './Components/Relative/Relative';
import Localization from './Components/Localization/Localization';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/circle" element={<Circle />} />
        <Route path="/experiment" element={<Experiment />} />
        <Route path="/quizz" element={<Relative />} />
        <Route path="/localization" element={<Localization />} />
      </Routes>
    </Router>
  );
}

export default App;
