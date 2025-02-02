import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, MessageSquare, Copy, Check } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const NoteDisplay = ({ transcription, summary, isLoading, onRequestSummary }) => {
  const [copied, setCopied] = useState(false);
  const [showFullText, setShowFullText] = useState(false);

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const renderTimestamp = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const truncateText = (text, maxLength = 300) => {
    if (!text || text.length <= maxLength) return text;
    return showFullText ? text : `${text.substring(0, maxLength)}...`;
  };

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardContent className="pt-6">
          <div className="flex items-center justify-center space-x-2">
            <Loader2 className="h-6 w-6 animate-spin" />
            <p>Processing audio...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!transcription) return null;

  return (
    <div className="space-y-4">
      <Card className="w-full">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-lg font-semibold">Transcription</CardTitle>
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(transcription.text)}
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              {truncateText(transcription.text)}
            </p>
            {transcription.text.length > 300 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowFullText(!showFullText)}
              >
                {showFullText ? 'Show Less' : 'Show More'}
              </Button>
            )}
            
            {transcription.segments && (
              <div className="mt-4 space-y-2">
                <p className="text-sm font-medium">Segments:</p>
                <div className="max-h-60 overflow-y-auto space-y-2">
                  {transcription.segments.map((segment, idx) => (
                    <div
                      key={idx}
                      className="text-sm p-2 bg-gray-50 rounded-md flex items-start space-x-2"
                    >
                      <span className="text-gray-500 min-w-[60px]">
                        {renderTimestamp(segment.start)}
                      </span>
                      <p className="flex-1">{segment.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {summary ? (
        <Card className="w-full">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">{summary.summary}</p>
            {summary.key_points && (
              <div className="mt-4">
                <p className="text-sm font-medium mb-2">Key Points:</p>
                <ul className="list-disc list-inside space-y-1">
                  {summary.key_points.map((point, idx) => (
                    <li key={idx} className="text-sm text-gray-600">{point}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        <Button
          onClick={onRequestSummary}
          className="w-full"
          variant="outline"
        >
          <MessageSquare className="mr-2 h-4 w-4" />
          Generate Summary
        </Button>
      )}
    </div>
  );
};

export default NoteDisplay;