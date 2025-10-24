import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import '../App.css';

interface LearningNote {
  id: number;
  title: string;
}

function DashboardPage() {
  const [notes, setNotes] = useState<LearningNote[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    const fetchNotes = async () => {
      if (!token) {
        setError('로그인이 필요합니다.');
        return;
      }

      setIsLoading(true);
      setError('');

      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL}/api/notes`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.status === 401) {
          throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
        }
        if (!response.ok) {
          throw new Error((await response.json()).detail || '학습 노트를 불러오는 중 오류 발생');
        }

        const data: LearningNote[] = await response.json();
        setNotes(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNotes();
  }, [token]);

  return (
    <header className="App-header">
      <h1>내 학습 노트</h1>
      {isLoading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      <div style={{ width: '80%', maxWidth: '1000px' }}>
        {notes.length > 0 ? (
          notes.map(note => (
            <Link to={`/notes/${note.id}`} key={note.id} className="summary-result-link">
              <div className="summary-result" style={{ textAlign: 'left', marginBottom: '1rem' }}>
                <p>{note.title}</p>
              </div>
            </Link>
          ))
        ) : (
          !isLoading && <p>아직 생성된 학습 노트가 없습니다.</p>
        )}
      </div>
    </header>
  );
}

export default DashboardPage;
