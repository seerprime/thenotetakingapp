import React, { useState, useRef } from 'react';
import { Mic, Square, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

const Recorder = ({ onRecordingComplete }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState(null);
  const mediaRecorder = useRef(null);
  const chunks = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      chunks.current = [];

      mediaRecorder.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.current.push(e.data);
        }
      };

      mediaRecorder.current.onstop = () => {
        const audioBlob = new Blob(chunks.current, { type: 'audio/wav' });
        onRecordingComplete(audioBlob);
      };

      mediaRecorder.current.start();
      setIsRecording(true);
      setError(null);
    } catch (err) {
      setError('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-4">
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <Button
            onClick={isRecording ? stopRecording : startRecording}
            variant={isRecording ? "destructive" : "default"}
            size="lg"
            className="rounded-full w-16 h-16 flex items-center justify-center"
          >
            {isRecording ? (
              <Square className="w-6 h-6" />
            ) : (
              <Mic className="w-6 h-6" />
            )}
          </Button>
          {isRecording && (
            <span className="absolute -top-2 -right-2 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
            </span>
          )}
        </div>
        <p className="text-sm text-gray-500">
          {isRecording ? 'Recording in progress...' : 'Click to start recording'}
        </p>
      </div>

      {error && (
        <Alert variant="destructive" className="mt-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default Recorder;