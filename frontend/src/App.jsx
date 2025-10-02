import { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";   // backend URL

export default function App() {  // main component reusable UI. 
// export default eans this the main thing this file exports. Like the app screen 
  const [number, setNumber] = useState(1);   // user input 
  // keeps track of the number input by the user, initialized to 1
  const [result, setResult] = useState(""); // backend reply
  // keeps track of the result received from the backend, initialized to an empty string
  const [error, setError] = useState("");
  // keeps track of any error messages, initialized to an empty string

  async function fetchResult() { // fetches result from backend
    try { // try catch block to handle errors
      setError(""); // clear previous error
      const res = await fetch(`${API_BASE}/api/number/${number}/`);  // actual fetch call to backend
      // await to wait for the fetch call to complete
      // res is a response object not the actual data
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      // if response is not ok, manually throw an error and send it to the catch block with status code
      const data = await res.json();
      // convert response to JSON format
      setResult(data.result);
      // update the react state with the result from the backend
    } catch (e) { // if error occurs, set error message
      setError(e.message);
    }
  }

  return (
    <div style={{ fontFamily: "system-ui", padding: 20 }}>
      <h1>BenchAnalytics</h1>

      <label>
        Select a group member (1–5):{" "}
        <input
          type="number"
          min="1"
          max="5"
          value={number}
          onChange={(e) => setNumber(e.target.value)}
        />
      </label>

      <button onClick={fetchResult}>Get member</button>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {result && (
        <p>
          <strong>Selected Member:</strong> {result}
        </p>
      )}
    </div>
  );
}