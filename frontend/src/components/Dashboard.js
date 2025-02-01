import React, { useState } from 'react';
import LogPanel from './LogPanel';
import Recorder from './Recorder';  // Import the Recorder component
import NoteDisplay from './NoteDisplay';

const Dashboard = () => {
  const [logs, setLogs] = useState([]);
  const [isQueryMode, setIsQueryMode] = useState(false);
  const [transcriptionResult, setTranscriptionResult] = useState('');

  const handleStartRecording = () => {
    setLogs([...logs, 'Recording started...']);
  };

  const handleStopRecording = async (audioBlob) => {
    setLogs([...logs, 'Recording stopped...']);
    const formData = new FormData();
    formData.append('audio', audioBlob);

    // Send the audio file to the backend for transcription
    const result = await fetch('/transcribe/', {
      method: 'POST',
      body: formData
    });

    const data = await result.json();
    setTranscriptionResult(data.transcription);
    setLogs([...logs, 'Transcription complete.']);
  };

  const handleSummarize = async () => {
    setLogs([...logs, 'Summarizing...']);
    const result = await fetch('/summarize/', { method: 'POST' });
    const data = await result.json();
    setTranscriptionResult(data.summary);
    setLogs([...logs, 'Summarization complete.']);
  };

  const handleQuery = async () => {
    setIsQueryMode(true);
    // Handle query input (Switch to query mode)
  };

  const handleStartNewTranscribe = () => {
    setTranscriptionResult('');
    setLogs([]);
    handleTranscribe();
  };

  return (
    <div className="dashboard">
      <LogPanel logs={logs} onQueryClick={handleQuery} onStartNewTranscribe={handleStartNewTranscribe} />
      <div className="main-content">
        {!isQueryMode && (
          <>
            <button onClick={handleTranscribe}>Transcribe</button>
            <button onClick={handleSummarize}>Summarize</button>
          </>
        )}
        {isQueryMode && <input type="text" placeholder="Enter your query" />}
        <NoteDisplay result={transcriptionResult} />
        
        {/* Add the Recorder component */}
        <Recorder onStartRecording={handleStartRecording} onStopRecording={handleStopRecording} />
      </div>
    </div>
  );
};

export default Dashboard;
