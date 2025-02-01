import { useState } from "react";
import { queryJarvis } from "../utils/api";

const ChatBot = () => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");

  const askJarvis = async () => {
    const answer = await queryJarvis(query, [0.1, 0.2, 0.3]);  // Placeholder embedding
    setResponse(answer);
  };

  return (
    <div>
      <h2>Ask Jarvis</h2>
      <input type="text" value={query} onChange={(e) => setQuery(e.target.value)} />
      <button onClick={askJarvis}>Ask</button>
      <p>{response}</p>
    </div>
  );
};

export default ChatBot;
