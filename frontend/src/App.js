import React, { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("");   // state for backend message
  const [loading, setLoading] = useState(true); // optional: loading state
  const [error, setError] = useState(null);     // optional: error handling

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/message/")
      .then(response => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then(data => {
        setMessage(data.message);  // store backend message in state
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching message:", err);
        setError(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading message...</p>;
  if (error) return <p>Error loading message!</p>;

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>{message}</h1>  {/* Display the backend message */}
    </div>
  );
}

export default App;
