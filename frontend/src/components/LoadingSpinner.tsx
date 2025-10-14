import React from 'react';

const LoadingSpinner: React.FC = () => {
  return (
    <div className="loading-spinner-container">
        <div className="loading-spinner"></div>
        <p>로딩 중...</p>
    </div>
  );
};

export default LoadingSpinner;
