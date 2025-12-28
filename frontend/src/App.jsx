import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import ChatInterface from './components/ChatInterface';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/chat"
            element={
              <ProtectedRoute>
                <ChatInterface />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/chat" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
