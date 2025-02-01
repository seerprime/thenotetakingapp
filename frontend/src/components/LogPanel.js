import React from 'react';

const LogPanel = ({ logs, onQueryClick, onStartNewTranscribe }) => {
  return (
    <div className="log-panel">
      <button onClick={onStartNewTranscribe}>Start New Transcribe</button>
      <button onClick={onQueryClick}>Query</button>
      <div className="logs">
        {logs.map((log, index) => (
          <p key={index}>{log}</p>
        ))}
      </div>
    </div>
  );
};

export default LogPanel;
