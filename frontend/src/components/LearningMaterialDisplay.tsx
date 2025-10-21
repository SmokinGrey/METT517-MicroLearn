import React from 'react';
import InteractiveQuiz from './InteractiveQuiz';
import FlippableFlashcard from './FlippableFlashcard';

// 데이터 타입 정의
interface QuizItem { question: string; options: string[]; answer: string; }
interface FlashcardItem { term: string; definition: string; }
interface LearningMaterial { summary: string; key_topics: string[]; quiz: QuizItem[]; flashcards: FlashcardItem[]; }
interface Props { materials: LearningMaterial; }

// 스타일 객체
const styles: { [key: string]: React.CSSProperties } = {
  guideContainer: {
    textAlign: 'left',
    backgroundColor: '#ffffff',
    color: '#20232a',
    padding: '2rem 3rem',
    borderRadius: '8px',
    boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
    marginTop: '2rem'
  },
  mainTitle: {
    fontSize: '2.5em',
    borderBottom: '2px solid #eee',
    paddingBottom: '0.5rem',
    marginBottom: '2rem',
    color: '#20232a'
  },
  section: {
    marginBottom: '2rem'
  },
  sectionTitle: {
    fontSize: '1.8em',
    color: '#61dafb',
    borderLeft: '4px solid #61dafb',
    paddingLeft: '0.8rem',
    marginBottom: '1.5rem'
  },
  bodyText: {
    fontSize: '1.1em',
    lineHeight: '1.8'
  },
  list: {
    fontSize: '1.1em',
    lineHeight: '1.8',
    paddingLeft: '2rem'
  },
  divider: {
    border: 'none',
    borderTop: '1px solid #eee',
    margin: '2rem 0'
  }
};

const LearningMaterialDisplay: React.FC<Props> = ({ materials }) => {
  return (
    <div style={styles.guideContainer}>
      <h1 style={styles.mainTitle}>종합 학습 가이드</h1>
      
      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>핵심 요약</h2>
        <p style={styles.bodyText}>{materials.summary}</p>
      </section>

      <hr style={styles.divider} />

      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>주요 주제</h2>
        <ul style={styles.list}>
          {materials.key_topics.map((topic, index) => (
            <li key={index}>{topic}</li>
          ))}
        </ul>
      </section>

      <hr style={styles.divider} />

      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>확인 퀴즈</h2>
        <InteractiveQuiz quiz={materials.quiz} />
      </section>

      <hr style={styles.divider} />

      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>핵심 용어 카드</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
          {materials.flashcards.map((item, index) => (
            <FlippableFlashcard key={index} term={item.term} definition={item.definition} />
          ))}
        </div>
      </section>
    </div>
  );
};

export default LearningMaterialDisplay;