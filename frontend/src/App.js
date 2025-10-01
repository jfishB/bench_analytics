import { useState } from "react";
import axios from "axios";

function App() {
  const [text, setText] = useState("");
  const [response, setResponse] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://127.0.0.1:8000/api/echo/", { text });
      setResponse(res.data.processed);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>React + Django Demo</h1>
      <form onSubmit={handleSubmit}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type something..."
        />
        <button type="submit">Send</button>
      </form>
      {response && <p>Backend says: {response}</p>}
    </div>
  );
}

export default App;