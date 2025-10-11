import React, { useState } from 'react';

interface QuizItem {
  question: string;
  options: string[];
  answer: string;
}

interface Props {
  quiz: QuizItem[];
}

const InteractiveQuiz: React.FC<Props> = ({ quiz }) => {
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [showResults, setShowResults] = useState<boolean>(false);

  const handleOptionSelect = (questionIndex: number, option: string) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: option,
    });
  };

  const getOptionStyle = (questionIndex: number, option: string) => {
    if (!showResults) return {};

    const correctAnswer = quiz[questionIndex].answer;
    const selectedAnswer = selectedAnswers[questionIndex];

    if (option === correctAnswer) {
      return { color: '#28a745', fontWeight: 'bold' }; // Green for correct answer
    }
    if (option === selectedAnswer && option !== correctAnswer) {
      return { color: '#dc3545' }; // Red for incorrect selection
    }
    return {};
  };

  return (
    <div>
      {quiz.map((item, index) => (
        <div key={index} style={{ marginBottom: '1.5rem', padding: '1rem', border: '1px solid #444', borderRadius: '8px' }}>
          <p><b>Q{index + 1}:</b> {item.question}</p>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
            {item.options.map((option, optionIndex) => (
              <button 
                key={optionIndex} 
                onClick={() => handleOptionSelect(index, option)}
                style={{
                  ...getOptionStyle(index, option),
                  margin: '0.25rem 0',
                  padding: '0.5rem',
                  border: `1px solid ${selectedAnswers[index] === option ? '#61dafb' : '#555'}`,
                  borderRadius: '4px',
                  background: 'none',
                  color: 'white',
                  textAlign: 'left',
                  cursor: 'pointer'
                }}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      ))}
      <button onClick={() => setShowResults(true)} style={{ marginTop: '1rem' }}>결과 확인</button>
    </div>
  );
};

export default InteractiveQuiz;
