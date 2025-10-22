// @ts-ignore
import React from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './components/Layout/MainLayout';
import Home from './pages/Home';
import ScorePage from './pages/ScorePage';
import EssayPage from './pages/EssayPage';
import TaskPage from './pages/TaskPage';
import AIPage from './pages/AIPage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Home />} />
          <Route path="scores" element={<ScorePage />} />
          <Route path="essays" element={<EssayPage />} />
          <Route path="tasks" element={<TaskPage />} />
          <Route path="ai" element={<AIPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
