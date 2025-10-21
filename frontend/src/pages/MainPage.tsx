import React, { useState, useRef } from 'react';
import '../App.css';
import { useAuthStore } from '../store/authStore';
import LearningMaterialDisplay from '../components/LearningMaterialDisplay';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';

// API 응답에 대한 타입 정의
interface QuizItem { question: string; options: string[]; answer: string; }
interface FlashcardItem { term: string; definition: string; }
interface LearningMaterial { summary: string; key_topics: string[]; quiz: QuizItem[]; flashcards: FlashcardItem[]; }

function MainPage() {
  const [activeTab, setActiveTab] = useState('text'); // 'text', 'file', 'url', 'youtube'
  const [inputText, setInputText] = useState<string>('');
  const [urlInput, setUrlInput] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [materials, setMaterials] = useState<LearningMaterial | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const token = useAuthStore((state) => state.token);

  // 공통 API 요청 핸들러
  const handleGenerate = async (endpoint: string, body: any, isFormData: boolean = false) => {
    if (!token) {
      setError('로그인이 필요합니다. 로그인 페이지로 이동하여 로그인해주세요.');
      return;
    }

    setIsLoading(true);
    setError('');
    setMaterials(null);

    try {
      const headers: HeadersInit = { 'Authorization': `Bearer ${token}` };
      if (!isFormData) {
        headers['Content-Type'] = 'application/json';
      }

      const response = await fetch(`${process.env.REACT_APP_API_URL}${endpoint}`, {
        method: 'POST',
        headers,
        body: isFormData ? body : JSON.stringify(body),
      });

      if (response.status === 401) throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '자료 생성 중 오류가 발생했습니다.');
      }

      const data: LearningMaterial = await response.json();
      setMaterials(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextGenerate = () => {
    if (!inputText.trim()) { setError('분석할 텍스트를 입력해주세요.'); return; }
    handleGenerate('/api/generate-materials', { text: inputText });
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files ? event.target.files[0] : null;
    setSelectedFile(file);
    if (file) setError('');
  };

  const handleFileGenerate = () => {
    if (!selectedFile) { setError('분석할 파일을 선택해주세요.'); return; }
    const formData = new FormData();
    formData.append('file', selectedFile);
    handleGenerate('/api/generate-materials-from-file', formData, true);
  };

  const handleUrlGenerate = () => {
    if (!urlInput.trim()) { setError('분석할 웹 페이지 주소를 입력해주세요.'); return; }
    handleGenerate('/api/generate-materials-from-url', { url: urlInput });
  };

  const handleYoutubeGenerate = () => {
    if (!urlInput.trim()) { setError('분석할 YouTube 영상 주소를 입력해주세요.'); return; }
    handleGenerate('/api/generate-materials-from-youtube', { url: urlInput });
  };

  const getTabStyle = (tabName: string) => ({
    all: 'unset', padding: '0.5rem 1rem', cursor: 'pointer', 
    borderBottom: activeTab === tabName ? '2px solid #61dafb' : '2px solid transparent', color: 'white'
  });

  const renderContent = () => {
    switch (activeTab) {
      case 'text':
        return <><textarea className="text-input" value={inputText} onChange={(e) => setInputText(e.target.value)} placeholder="여기에 학습할 내용을 붙여넣으세요..." rows={10} /><button onClick={handleTextGenerate} disabled={isLoading}>{isLoading ? '생성 중...' : '학습 자료 생성'}</button></>;
      case 'file':
        return <><input type="file" ref={fileInputRef} onChange={handleFileChange} style={{ display: 'none' }} accept=".txt,.pdf,.docx" /><button onClick={() => fileInputRef.current?.click()} disabled={isLoading}>파일 선택</button>{selectedFile && <p className="file-name">선택된 파일: {selectedFile.name}</p>}<button onClick={handleFileGenerate} disabled={!selectedFile || isLoading}>{isLoading ? '생성 중...' : '학습 자료 생성'}</button></>;
      case 'url':
        return <><input type="text" className="text-input" value={urlInput} onChange={(e) => setUrlInput(e.target.value)} placeholder="웹 페이지 주소를 여기에 붙여넣으세요..." /><button onClick={handleUrlGenerate} disabled={isLoading}>{isLoading ? '생성 중...' : '학습 자료 생성'}</button></>;
      case 'youtube':
        return <><input type="text" className="text-input" value={urlInput} onChange={(e) => setUrlInput(e.target.value)} placeholder="YouTube 영상 주소를 여기에 붙여넣으세요..." /><button onClick={handleYoutubeGenerate} disabled={isLoading}>{isLoading ? '생성 중...' : '학습 자료 생성'}</button></>;
      default: return null;
    }
  };

  return (
    <header className="App-header">
      <h1>MicroLearn AI</h1>
      <div className="summarize-container" style={{ width: '80%', maxWidth: '1000px' }}>
        <div style={{ display: 'flex', borderBottom: '1px solid #555', marginBottom: '1rem' }}>
            <button onClick={() => setActiveTab('text')} style={getTabStyle('text')}>텍스트 입력</button>
            <button onClick={() => setActiveTab('file')} style={getTabStyle('file')}>파일 업로드</button>
            <button onClick={() => setActiveTab('url')} style={getTabStyle('url')}>웹 페이지</button>
            <button onClick={() => setActiveTab('youtube')} style={getTabStyle('youtube')}>YouTube</button>
        </div>
        {renderContent()}
      </div>
      
      {isLoading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}

      {!isLoading && materials && <LearningMaterialDisplay materials={materials} />}    </header>
  );
}

export default MainPage;