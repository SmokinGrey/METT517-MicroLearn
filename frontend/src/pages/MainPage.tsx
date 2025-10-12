import React, { useState, useRef } from 'react';
import '../App.css';
import { useAuthStore } from '../store/authStore';
import LearningMaterialDisplay from '../components/LearningMaterialDisplay';

// API 응답에 대한 타입 정의
interface QuizItem {
  question: string;
  options: string[];
  answer: string;
}

interface FlashcardItem {
  term: string;
  definition: string;
}

interface LearningMaterial {
  summary: string;
  key_topics: string[];
  quiz: QuizItem[];
  flashcards: FlashcardItem[];
}

function MainPage() {
  const [activeTab, setActiveTab] = useState('text'); // 'text' or 'file'
  const [inputText, setInputText] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [materials, setMaterials] = useState<LearningMaterial | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const token = useAuthStore((state) => state.token);

  const handleTextGenerate = async () => {
    if (!inputText.trim()) {
      setError('분석할 텍스트를 입력해주세요.');
      return;
    }
    if (!token) {
      setError('로그인이 필요합니다. 로그인 페이지로 이동하여 로그인해주세요.');
      return;
    }

    setIsLoading(true);
    setError('');
    setMaterials(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/generate-materials', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ text: inputText }),
      });

      if (response.status === 401) {
        throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
      }
      if (!response.ok) {
        throw new Error((await response.json()).detail || '자료 생성 중 오류 발생');
      }

      const data: LearningMaterial = await response.json();
      setMaterials(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files ? event.target.files[0] : null;
    setSelectedFile(file);
    if (file) {
        setError('');
    }
  };

  const handleFileGenerate = async () => {
    if (!selectedFile) {
      setError('분석할 파일을 선택해주세요.');
      return;
    }
    if (!token) {
      setError('로그인이 필요합니다. 로그인 페이지로 이동하여 로그인해주세요.');
      return;
    }

    setIsLoading(true);
    setError('');
    setMaterials(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/generate-materials-from-file', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.status === 401) {
        throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
      }
      if (!response.ok) {
        throw new Error((await response.json()).detail || '자료 생성 중 오류 발생');
      }

      const data: LearningMaterial = await response.json();
      setMaterials(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <header className="App-header">
      <h1>MicroLearn AI</h1>
      <div className="summarize-container" style={{ width: '80%', maxWidth: '1000px' }}>
        <div style={{ display: 'flex', borderBottom: '1px solid #555', marginBottom: '1rem' }}>
            <button onClick={() => setActiveTab('text')} style={{ all: 'unset', padding: '0.5rem 1rem', cursor: 'pointer', borderBottom: activeTab === 'text' ? '2px solid #61dafb' : '2px solid transparent' }}>텍스트 입력</button>
            <button onClick={() => setActiveTab('file')} style={{ all: 'unset', padding: '0.5rem 1rem', cursor: 'pointer', borderBottom: activeTab === 'file' ? '2px solid #61dafb' : '2px solid transparent' }}>파일 업로드</button>
        </div>

        {activeTab === 'text' ? (
          <>
            <textarea
              className="text-input"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="여기에 학습할 내용을 붙여넣으세요..."
              rows={10}
            />
            <button onClick={handleTextGenerate} disabled={isLoading}>{isLoading ? '생성 중...' : '학습 자료 생성'}</button>
          </>
        ) : (
          <>
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                style={{ display: 'none' }}
                accept=".txt,.pdf,.docx"
            />
            <button onClick={() => fileInputRef.current?.click()} disabled={isLoading}>파일 선택</button>
            {selectedFile && <p className="file-name">선택된 파일: {selectedFile.name}</p>}
            <button onClick={handleFileGenerate} disabled={!selectedFile || isLoading}>{isLoading ? '생성 중...' : '학습 자료 생성'}</button>
          </>  
        )}
      </div>
      
      {error && <p className="error-message">{error}</p>}

      {materials && <LearningMaterialDisplay materials={materials} />}
    </header>
  );
}

export default MainPage;
