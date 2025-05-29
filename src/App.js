import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import PredictionPage from './pages/PredictionPage';
import './App.css';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/predict" element={<PredictionPage />} />
            </Routes>
        </Router>
    );
}

export default App;
