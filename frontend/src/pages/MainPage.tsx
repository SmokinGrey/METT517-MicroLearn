import React, { useState, useRef } from 'react';
import '../App.css';

function MainPage() {
  // State for text input summarization
  const [inputText, setInputText] = useState<string>('');
  
  // State for file upload summarization
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Common state for results and loading/error
  const [summary, setSummary] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // Handler for text input summarization
  const handleTextSummarize = async () => {
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
      });
      if (!response.ok) throw new Error((await response.json()).detail || '요약 중 오류 발생');
      const data = await response.json();
      setSummary(data.summary);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handler for file selection
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files ? event.target.files[0] : null;
    setSelectedFile(file);
    if (file) {
        setError(''); // Clear previous errors on new file selection
    }
  };

  // Handler for file upload summarization
  const handleFileSummarize = async () => {
    if (!selectedFile) {
      setError('요약할 파일을 선택해주세요.');
      return;
    }
    setIsLoading(true);
    setError('');
    setSummary('');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/upload-and-summarize', {
        method: 'POST',
        body: formData, // Browser sets Content-Type automatically for FormData
      });
      if (!response.ok) throw new Error((await response.json()).detail || '파일 요약 중 오류 발생');
      const data = await response.json();
      setSummary(data.summary);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <header className="App-header">
      <h1>MicroLearn AI</h1>
      
      <div className="summarize-container text-summarize">
        <h2>텍스트로 요약하기</h2>
        <textarea
          className="text-input"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="여기에 텍스트를 붙여넣으세요..."
          rows={8}
        />
        <button onClick={handleTextSummarize} disabled={isLoading}>
          {isLoading ? '요약 중...' : '텍스트 요약'}
        </button>
      </div>

      <div className="summarize-container file-summarize">
          <h2>파일로 요약하기</h2>
          <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              style={{ display: 'none' }}
              accept=".txt,.pdf,.docx"
          />
          <button onClick={() => fileInputRef.current?.click()} disabled={isLoading}>
              파일 선택
          </button>
          {selectedFile && <p className="file-name">선택된 파일: {selectedFile.name}</p>}
          <button onClick={handleFileSummarize} disabled={!selectedFile || isLoading}>
              {isLoading ? '업로드 및 요약 중...' : '파일 업로드 및 요약'}
          </button>
      </div>
      
      {error && <p className="error-message">{error}</p>}

      {summary && (
        <div className="summary-result">
          <h2>요약 결과:</h2>
          <p className="summary-text">{summary}</p>
        </div>
      )}
    </header>
  );
}

export default MainPage;
