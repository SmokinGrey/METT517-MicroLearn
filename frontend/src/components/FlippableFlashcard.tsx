import React, { useState } from 'react';

interface Props {
  term: string;
  definition: string;
}

const FlippableFlashcard: React.FC<Props> = ({ term, definition }) => {
  const [isFlipped, setIsFlipped] = useState(false);

  return (
    <div 
      className={`flashcard-container ${isFlipped ? 'flipped' : ''}`}
      onClick={() => setIsFlipped(!isFlipped)}
    >
      <div className="flashcard-inner">
        <div className="flashcard-front">
          {term}
        </div>
        <div className="flashcard-back">
          {definition}
        </div>
      </div>
    </div>
  );
};

export default FlippableFlashcard;
