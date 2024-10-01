import React from 'react';
import { BrowserRouter as Router,Routes, Route} from 'react-router-dom';
import RecommendPage from './pages/RecommendPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<RecommendPage />}/>
      </Routes>
    </Router>
  );
}

export default App;
