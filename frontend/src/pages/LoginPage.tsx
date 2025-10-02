import React, { useState } from 'react';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleLogin = async () => {
    setMessage('');
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch('http://127.0.0.1:8000/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || '로그인에 실패했습니다.');
      }

      // TODO: 발급받은 토큰(data.access_token)을 저장하는 로직 추가
      console.log('Access Token:', data.access_token);
      setMessage('로그인 성공! 토큰이 콘솔에 출력되었습니다.');

    } catch (error: any) {
      setMessage(error.message);
    }
  };

  return (
    <header className="App-header">
      <div className="summarize-container">
        <h2>로그인</h2>
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
        <button onClick={handleLogin}>로그인</button>
        {message && <p style={{ marginTop: '1rem', fontSize: '1rem' }}>{message}</p>}
      </div>
    </header>
  );
}

export default LoginPage;