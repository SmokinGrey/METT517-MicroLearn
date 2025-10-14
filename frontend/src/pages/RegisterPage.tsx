import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function RegisterPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleRegister = async () => {
    setMessage('');
    try {
      const response = await fetch('http://127.0.0.1:8000/users/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || '회원가입에 실패했습니다.');
      }

      setMessage(`회원가입 성공! ${data.username}님, 잠시 후 로그인 페이지로 이동합니다.`);
      setUsername('');
      setPassword('');

      setTimeout(() => {
        navigate('/login');
      }, 2000); // 2초 후 로그인 페이지로 이동

    } catch (error: any) {
      setMessage(error.message);
    }
  };

  return (
    <header className="App-header">
      <div className="summarize-container">
        <h2>회원가입</h2>
        <input
          type="text"
          placeholder="사용자 아이디"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="text-input"
          style={{ marginBottom: '1rem' }}
        />
        <input
          type="password"
          placeholder="비밀번호"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="text-input"
          style={{ marginBottom: '1rem' }}
        />
        <button onClick={handleRegister}>회원가입</button>
        {message && <p style={{ marginTop: '1rem', fontSize: '1rem' }}>{message}</p>}
      </div>
    </header>
  );
}

export default RegisterPage;