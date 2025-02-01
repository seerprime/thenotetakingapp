import { useEffect, useState } from "react";
import { getKeyPoints } from "../utils/api";

const NoteDisplay = ({ text }) => {
  const [keyPoints, setKeyPoints] = useState([]);

  useEffect(() => {
    if (text) {
      getKeyPoints(text).then(setKeyPoints);
    }
  }, [text]);

  return (
    <div>
      <h2>Transcription</h2>
      <p>{text}</p>
      <h2>Key Points</h2>
      <ul>
        {keyPoints.map((point, index) => (
          <li key={index}>{point}</li>
        ))}
      </ul>
    </div>
  );
};

export default NoteDisplay;
