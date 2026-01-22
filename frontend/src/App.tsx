import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import CaptureScreen from './pages/CaptureScreen';
import ReviewExtraction from './pages/ReviewExtraction';
import MatchPo from './pages/MatchPo';
import MatchLines from './pages/MatchLines';
import ConfirmReceipt from './pages/ConfirmReceipt';
import ReceiptResult from './pages/ReceiptResult';
import ReceiptHistory from './pages/ReceiptHistory';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/capture" element={<CaptureScreen />} />
        <Route path="/review" element={<ReviewExtraction />} />
        <Route path="/match-po" element={<MatchPo />} />
        <Route path="/match-lines" element={<MatchLines />} />
        <Route path="/confirm" element={<ConfirmReceipt />} />
        <Route path="/result" element={<ReceiptResult />} />
        <Route path="/history" element={<ReceiptHistory />} />
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  );
}

export default App;
