import { useState } from "react";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";
import { uploadAudio } from "../utils/api";

const Recorder = ({ setText }) => {
  const { transcript, listening, resetTranscript } = useSpeechRecognition();
  const [file, setFile] = useState(null);

  const startListening = () => {
    resetTranscript();
    SpeechRecognition.startListening({ continuous: true });
  };

  const stopListening = async () => {
    SpeechRecognition.stopListening();
    setText(transcript);
  };

  const handleUpload = async () => {
    if (file) {
      const text = await uploadAudio(file);
      setText(text);
    }
  };

  return (
    <div>
      <button onClick={startListening}>🎤 Start</button>
      <button onClick={stopListening}>⏹ Stop</button>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>📤 Upload</button>
      <p>{listening ? "Listening..." : "Click to start"}</p>
    </div>
  );
};

export default Recorder;
