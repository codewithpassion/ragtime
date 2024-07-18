import React from 'react';
import './App.css';
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <div className="h-screen flex flex-col">
      <h1 className="p-4 bg-gray-800 text-white">RAG</h1>
      <div className="flex-1">
        <ChatInterface />
      </div>
    </div>
  );
}

export default App;
