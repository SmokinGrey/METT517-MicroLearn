import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import LearningMaterialDisplay from '../components/LearningMaterialDisplay';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import '../App.css';

// API 응답에 대한 타입 정의 (기존 페이지들과 공유 가능)
interface QuizItem {
  question: string;
  options: string[];
  answer: string;
}

interface FlashcardItem {
  term: string;
  definition: string;
}

interface KeyTopic {
    id: number;
    topic: string;
}

interface LearningMaterial {
  id: number;
  summary: string;
  key_topics: KeyTopic[];
  quiz_items: QuizItem[];
  flashcards: FlashcardItem[];
}

// LearningMaterialDisplay props 타입에 맞게 변환하는 함수
const transformMaterialData = (data: LearningMaterial) => {
    return {
        summary: data.summary,
        key_topics: data.key_topics.map(kt => kt.topic),
        quiz: data.quiz_items,
        flashcards: data.flashcards,
    };
};

function MaterialDetailPage() {
  const { material_id } = useParams<{ material_id: string }>();
  const [material, setMaterial] = useState<LearningMaterial | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    const fetchMaterial = async () => {
      if (!token) {
        setError('로그인이 필요합니다.');
        return;
      }
      if (!material_id) {
        setError('유효하지 않은 자료 ID입니다.');
        return;
      }

      setIsLoading(true);
      setError('');

      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL}/api/materials/${material_id}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.status === 401) {
          throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
        }
        if (response.status === 404) {
            throw new Error('해당 자료를 찾을 수 없거나 접근 권한이 없습니다.');
        }
        if (!response.ok) {
          throw new Error((await response.json()).detail || '자료를 불러오는 중 오류 발생');
        }

        const data: LearningMaterial = await response.json();
        setMaterial(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMaterial();
  }, [material_id, token]);

  return (
    <header className="App-header">
      {isLoading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {material && (
          <div style={{ width: '80%', maxWidth: '1000px' }}>
              <LearningMaterialDisplay materials={transformMaterialData(material)} />
          </div>
      )}
    </header>
  );
}

export default MaterialDetailPage;
