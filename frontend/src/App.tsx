import React from 'react';
import { Route, Routes, Link } from 'react-router-dom';
import './App.css';
import MainPage from './pages/MainPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

function App() {
  return (
    <div className="App">
      <nav style={{ padding: '1rem', backgroundColor: '#20232a', textAlign: 'left' }}>
        <Link to="/" style={{ color: 'white', marginRight: '1rem' }}>메인</Link>
        <Link to="/login" style={{ color: 'white', marginRight: '1rem' }}>로그인</Link>
        <Link to="/register" style={{ color: 'white' }}>회원가입</Link>
      </nav>
      <Routes>
          <Route path="/" element={<MainPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
      </Routes>
    </div>
  );
}

export default App;
