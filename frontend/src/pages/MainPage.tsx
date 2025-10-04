import React, { useState } from 'react';
import '../App.css';
import { useAuthStore } from '../store/authStore';

// 임시: 스키마를 공유하지 않으므로 프론트엔드에서 직접 타입을 정의합니다.
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
  const [inputText, setInputText] = useState<string>('');
  const [materials, setMaterials] = useState<LearningMaterial | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const token = useAuthStore((state) => state.token);

  const handleGenerate = async () => {
    if (!inputText.trim()) {
      setError('분석할 텍스트를 입력해주세요.');
      return;
    }
    if (!token) {
      setError('로그인이 필요합니다.');
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

  return (
    <header className="App-header">
      <h1>MicroLearn AI</h1>
      <div className="summarize-container" style={{ width: '80%', maxWidth: '1000px' }}>
        <h2>학습 자료 생성</h2>
        <textarea
          className="text-input"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="여기에 학습할 내용을 붙여넣으세요..."
          rows={10}
        />
        <button onClick={handleGenerate} disabled={isLoading}>
          {isLoading ? '생성 중...' : '학습 자료 생성'}
        </button>
      </div>
      
      {error && <p className="error-message">{error}</p>}

      {materials && (
        <div className="summary-result" style={{ textAlign: 'left' }}>
          <h2>요약</h2>
          <p>{materials.summary}</p>

          <h2 style={{ marginTop: '2rem' }}>핵심 주제</h2>
          <ul>
            {materials.key_topics.map((topic, index) => (
              <li key={index}>{topic}</li>
            ))}
          </ul>

          <h2 style={{ marginTop: '2rem' }}>자동 생성 퀴즈</h2>
          {materials.quiz.map((item, index) => (
            <div key={index} style={{ marginBottom: '1rem' }}>
              <p><b>Q{index + 1}:</b> {item.question}</p>
              <p><em>(정답: {item.answer})</em></p>
            </div>
          ))}

          <h2 style={{ marginTop: '2rem' }}>자동 생성 용어 카드</h2>
          {materials.flashcards.map((item, index) => (
            <div key={index} style={{ marginBottom: '1rem' }}>
              <p><b>{item.term}:</b> {item.definition}</p>
            </div>
          ))}
        </div>
      )}
    </header>
  );
}

export default MainPage;
