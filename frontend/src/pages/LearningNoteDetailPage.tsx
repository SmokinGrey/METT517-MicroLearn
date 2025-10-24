import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import ChatInterface from '../components/ChatInterface'; // Placeholder for now
import '../App.css';

interface Source {
  id: number;
  type: 'file' | 'url' | 'text' | 'youtube';
  path: string;
}

interface LearningNote {
  id: number;
  title: string;
  sources: Source[];
}

function LearningNoteDetailPage() {
  const { note_id } = useParams<{ note_id: string }>();
  const [note, setNote] = useState<LearningNote | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    const fetchNoteDetails = async () => {
      if (!token || !note_id) {
        setError('잘못된 접근입니다.');
        return;
      }

      setIsLoading(true);
      setError('');

      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL}/api/notes/${note_id}`, {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${token}` },
        });

        if (response.status === 401) throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
        if (!response.ok) throw new Error((await response.json()).detail || '노트 정보를 불러오는 중 오류 발생');

        const data: LearningNote = await response.json();
        setNote(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNoteDetails();
  }, [note_id, token]);

  const handleAddSource = () => {
    // TODO: Implement UI for adding new sources (file, url, etc.)
    alert('소스 추가 기능은 아직 구현되지 않았습니다.');
  };
  
  const handleAnalyzeNote = () => {
    // TODO: Implement the comprehensive analysis call
    alert('노트 종합 분석 기능은 아직 구현되지 않았습니다.');
  };

  if (isLoading) return <div className="App-header"><LoadingSpinner /></div>;
  if (error) return <div className="App-header"><ErrorMessage message={error} /></div>;
  if (!note) return <div className="App-header"><p>노트를 찾을 수 없습니다.</p></div>;

  return (
    <div className="App-header" style={{ display: 'flex', flexDirection: 'row', alignItems: 'flex-start' }}>
      <div style={{ flex: 1, padding: '2rem' }}>
        <h1>{note.title}</h1>
        
        <div className="sources-section">
          <h2>학습 소스</h2>
          <button onClick={handleAddSource} style={{marginBottom: '1rem'}}>+ 소스 추가</button>
          <button onClick={handleAnalyzeNote} style={{marginBottom: '1rem', marginLeft: '1rem'}}>노트 종합 분석</button>
          {note.sources.length > 0 ? (
            <ul>
              {note.sources.map(source => (
                <li key={source.id}>[{source.type}] {source.path}</li>
              ))}
            </ul>
          ) : (
            <p>이 노트에 추가된 소스가 없습니다.</p>
          )}
        </div>

        <div className="material-section">
          <h2>생성된 학습 자료</h2>
          {/* TODO: Display generated materials (summary, quiz, etc.) */}
          <p>종합 분석 결과가 여기에 표시됩니다.</p>
        </div>
      </div>

      <div style={{ flex: 1, padding: '2rem', borderLeft: '1px solid #444', height: '100vh' }}>
        <ChatInterface noteId={note.id} />
      </div>
    </div>
  );
}

export default LearningNoteDetailPage;
