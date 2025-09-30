import React, { useState } from 'react';
import './App.css';

function App() {
  const [inputText, setInputText] = useState<string>('');
  const [summary, setSummary] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const handleSummarize = async () => {
    if (!inputText.trim()) {
      setError('요약할 텍스트를 입력해주세요.');
      return;
    }
    setIsLoading(true);
    setError('');
    setSummary('');

    try {
      const response = await fetch('http://127.0.0.1:8000/api/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputText }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '요약 중 오류가 발생했습니다.');
      }

      const data = await response.json();
      setSummary(data.summary);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>MicroLearn AI - 텍스트 요약</h1>
        <p>요약하고 싶은 텍스트를 아래에 입력하세요.</p>
        <textarea
          className="text-input"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="여기에 텍스트를 붙여넣으세요..."
          rows={10}
          cols={80}
        />
        <button 
          className="summarize-button" 
          onClick={handleSummarize} 
          disabled={isLoading}
        >
          {isLoading ? '요약 중...' : '요약하기'}
        </button>
        
        {error && <p className="error-message">{error}</p>}

        {summary && (
          <div className="summary-container">
            <h2>요약 결과:</h2>
            <p className="summary-text">{summary}</p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;