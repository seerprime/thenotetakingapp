import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';
import Recorder from './components/Recorder';
import NoteDisplay from './components/NoteDisplay';
import ChatBot from './components/ChatBot';

const App = () => {
  const [currentNoteId, setCurrentNoteId] = useState(null);
  const [transcription, setTranscription] = useState(null);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleRecordingComplete = async (audioBlob) => {
    setIsLoading(true);
    setError(null);

    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.wav');

      // Send to transcription API
      const response = await fetch('/api/transcribe', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        setTranscription(data.result);
        
        // Store in database and get note ID
        const noteResponse = await fetch('/api/notes', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            content: data.result.text,
            segments: data.result.segments,
          }),
        });

        const noteData = await noteResponse.json();
        if (noteData.success) {
          setCurrentNoteId(noteData.note_id);
        }
      } else {
        throw new Error(data.error);
      }
    } catch (err) {
      setError('Failed to process recording. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRequestSummary = async () => {
    if (!transcription?.text) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: transcription.text,
          note_id: currentNoteId,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setSummary(data.result);
      } else {
        throw new Error(data.error);
      }
    } catch (err) {
      setError('Failed to generate summary. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="container mx-auto max-w-4xl space-y-8">
        <header className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">Jarvis Notes</h1>
          <p className="text-muted-foreground mt-2">
            Record, transcribe, and analyze your notes with AI
          </p>
        </header>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Card>
          <CardContent className="p-6">
            <Recorder onRecordingComplete={handleRecordingComplete} />
          </CardContent>
        </Card>

        <Tabs defaultValue="notes" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="notes">Notes</TabsTrigger>
            <TabsTrigger value="chat">Chat</TabsTrigger>
          </TabsList>
          
          <TabsContent value="notes">
            <NoteDisplay
              transcription={transcription}
              summary={summary}
              isLoading={isLoading}
              onRequestSummary={handleRequestSummary}
            />
          </TabsContent>
          
          <TabsContent value="chat">
            {currentNoteId ? (
              <ChatBot noteId={currentNoteId} />
            ) : (
              <Card>
                <CardContent className="p-6 text-center text-muted-foreground">
                  Record or transcribe some notes first to start chatting
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default App;