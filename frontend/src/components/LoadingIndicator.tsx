import React from 'react';

const LoadingIndicator = () => {
  return (
    <div className="flex justify-start">
      <div className="bg-blue-500 rounded-lg p-3 animate-pulse">
        🤖
      </div>
    </div>
  );
};

export default LoadingIndicator;
