import { useState } from "react";

function App() {
  const [msg, setMsg] = useState("");

  const fetchHello = async () => {
    const res = await fetch("http://localhost:8000/api/hello/");
    const data = await res.json();
    setMsg(data.message);
  };

  return (
    <div style={{ padding: 24, fontFamily: "system-ui, sans-serif" }}>
      <h1>React ↔ Django</h1>
      <button onClick={fetchHello}>Get message from backend</button>
      <p style={{ marginTop: 12 }}>{msg}</p>
    </div>
  );
}

export default App;
