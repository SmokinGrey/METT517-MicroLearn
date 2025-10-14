import React from 'react';
import { Route, Routes, Link, useNavigate } from 'react-router-dom';
import './App.css';
import MainPage from './pages/MainPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage'; // 대시보드 페이지 임포트
import MaterialDetailPage from './pages/MaterialDetailPage'; // 상세 페이지 임포트
import { useAuthStore } from './store/authStore';

function App() {
  const { token, clearToken } = useAuthStore((state) => state);
  const navigate = useNavigate();

  const handleLogout = () => {
    clearToken();
    navigate('/login');
  };

  return (
    <div className="App">
      <nav style={{ padding: '1rem', backgroundColor: '#20232a', textAlign: 'left' }}>
        <Link to="/" style={{ color: 'white', marginRight: '1rem' }}>메인</Link>
        {token ? (
          <>
            <Link to="/dashboard" style={{ color: 'white', marginRight: '1rem' }}>대시보드</Link>
            <button onClick={handleLogout} style={{ color: 'white', background: 'none', border: 'none', cursor: 'pointer', fontSize: '1em' }}>로그아웃</button>
          </>
        ) : (
          <>
            <Link to="/login" style={{ color: 'white', marginRight: '1rem' }}>로그인</Link>
            <Link to="/register" style={{ color: 'white' }}>회원가입</Link>
          </>
        )}
      </nav>
      <Routes>
          <Route path="/" element={<MainPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/materials/:material_id" element={<MaterialDetailPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
      </Routes>
    </div>
  );
}

export default App;
