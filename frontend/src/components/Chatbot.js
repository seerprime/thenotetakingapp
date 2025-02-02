import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';

const ChatBot = ({ noteId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage,
          note_id: noteId
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setMessages(prev => [...prev, {
          type: 'assistant',
          content: data.result.answer,
          sources: data.result.sources
        }]);

        // Get follow-up questions
        if (data.result.sources.length > 0) {
          const questionsResponse = await fetch('/api/suggest-questions', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              query: userMessage,
              answer: data.result.answer,
              context: data.result.sources.map(s => s.content).join('\n')
            }),
          });

          const questionsData = await questionsResponse.json();
          if (questionsData.success && questionsData.questions.length > 0) {
            setMessages(prev => [...prev, {
              type: 'suggestions',
              content: questionsData.questions
            }]);
          }
        }
      } else {
        throw new Error(data.error);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'Sorry, I encountered an error processing your question.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (question) => {
    setInput(question);
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const renderMessage = (message, idx) => {
    switch (message.type) {
      case 'user':
        return (
          <div className="flex justify-end mb-4">
            <div className="bg-primary text-primary-foreground rounded-lg py-2 px-4 max-w-[80%]">
              <p className="text-sm">{message.content}</p>
            </div>
          </div>
        );
      
      case 'assistant':
        return (
          <div className="flex flex-col space-y-2 mb-4">
            <div className="bg-secondary rounded-lg py-2 px-4 max-w-[80%]">
              <p className="text-sm">{message.content}</p>
            </div>
            {message.sources && message.sources.length > 0 && (
              <div className="text-xs text-gray-500 ml-4">
                <p className="font-medium">Sources:</p>
                {message.sources.map((source, i) => (
                  <div key={i} className="mt-1">
                    {source.timestamp && (
                      <span className="text-primary">
                        [{Math.floor(source.timestamp.start)}s - {Math.floor(source.timestamp.end)}s]
                      </span>
                    )}
                    <p className="ml-2 line-clamp-1">{source.content}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      
      case 'suggestions':
        return (
          <div className="flex flex-wrap gap-2 mb-4">
            {message.content.map((question, i) => (
              <Button
                key={i}
                variant="outline"
                size="sm"
                onClick={() => handleSuggestionClick(question)}
                className="text-xs"
              >
                {question}
              </Button>
            ))}
          </div>
        );
      
      case 'error':
        return (
          <div className="flex justify-start mb-4">
            <div className="bg-destructive/10 text-destructive rounded-lg py-2 px-4 max-w-[80%]">
              <p className="text-sm">{message.content}</p>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <Card className="w-full h-[600px] flex flex-col">
      <CardHeader>
        <CardTitle>Ask Questions</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col">
        <ScrollArea className="flex-1 pr-4">
          <div className="space-y-4">
            {messages.map((message, idx) => (
              <div key={idx}>{renderMessage(message, idx)}</div>
            ))}
            {isLoading && (
              <div className="flex items-center justify-center py-2">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            )}
          </div>
        </ScrollArea>
        
        <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your notes..."
            disabled={isLoading}
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default ChatBot;