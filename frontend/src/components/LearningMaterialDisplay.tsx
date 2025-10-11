import React from 'react';
import InteractiveQuiz from './InteractiveQuiz';
import FlippableFlashcard from './FlippableFlashcard';

// MainPage에서 전달받을 데이터 타입 정의
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

interface Props {
  materials: LearningMaterial;
}

const LearningMaterialDisplay: React.FC<Props> = ({ materials }) => {
  return (
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
      <InteractiveQuiz quiz={materials.quiz} />

      <h2 style={{ marginTop: '2rem' }}>자동 생성 용어 카드</h2>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
        {materials.flashcards.map((item, index) => (
          <FlippableFlashcard key={index} term={item.term} definition={item.definition} />
        ))}
      </div>
    </div>
  );
};

export default LearningMaterialDisplay;
