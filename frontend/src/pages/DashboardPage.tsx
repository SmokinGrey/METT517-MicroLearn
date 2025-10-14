import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import '../App.css';

interface LearningMaterial {
  id: number;
  summary: string;
  owner_id: number;
  key_topics: any[];
  quiz_items: any[];
  flashcards: any[];
}

function DashboardPage() {
  const [materials, setMaterials] = useState<LearningMaterial[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    const fetchMaterials = async () => {
      if (!token) {
        setError('로그인이 필요합니다.');
        return;
      }

      setIsLoading(true);
      setError('');

      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL}/api/my-materials`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.status === 401) {
          throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
        }
        if (!response.ok) {
          throw new Error((await response.json()).detail || '자료를 불러오는 중 오류 발생');
        }

        const data: LearningMaterial[] = await response.json();
        setMaterials(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMaterials();
  }, [token]);

  return (
    <header className="App-header">
      <h1>내 학습 자료</h1>
      {isLoading && <p>로딩 중...</p>}
      {error && <p className="error-message">{error}</p>}
      <div style={{ width: '80%', maxWidth: '1000px' }}>
        {materials.length > 0 ? (
          materials.map(material => (
            <Link to={`/materials/${material.id}`} key={material.id} className="summary-result-link">
              <div className="summary-result" style={{ textAlign: 'left', marginBottom: '1rem' }}>
                <p>{material.summary.substring(0, 200)}...</p>
              </div>
            </Link>
          ))
        ) : (
          !isLoading && <p>아직 생성된 학습 자료가 없습니다.</p>
        )}
      </div>
    </header>
  );
}

export default DashboardPage;
