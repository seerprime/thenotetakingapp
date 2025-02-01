// MAIN UI

import { useState } from "react";
import Recorder from "./components/Recorder";
import NoteDisplay from "./components/NoteDisplay";
import ChatBot from "./components/ChatBot";
import "./styles.css";

function App() {
  const [text, setText] = useState("");

  return (
    <div className="container">
      <h1>Jarvis Notes</h1>
      <Recorder setText={setText} />
      <NoteDisplay text={text} />
      <ChatBot />
    </div>
  );
}

export default App;
