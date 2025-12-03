import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "../../services/authService";

export default function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await authService.register({ username, email, password });
      setMessage("✅ Registration successful! You can now log in.");
      setUsername("");
      setEmail("");
      setPassword("");
    } catch (err: any) {
      // Slices Message to remove "Error: " prefix and trailing }
      setMessage(`❌ ${err.message.slice(9, -1) || "Registration failed"}`);
    }
  };

  return (
    <div className="flex flex-col items-center mt-10">
      <form
        onSubmit={handleRegister}
        className="bg-white p-8 rounded-2xl shadow-md w-96"
      >
        <h2 className="text-2xl font-bold mb-6 text-center">Register</h2>

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="border w-full p-2 mb-3 rounded"
          required
        />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border w-full p-2 mb-3 rounded"
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border w-full p-2 mb-4 rounded"
          required
        />

        <button
          type="submit"
          className="bg-blue-700 text-white w-full py-2 rounded !hover:bg-blue-800"
        >
          Register
        </button>

        {message && (
          <p className="text-center mt-4 text-sm text-gray-700">{message}</p>
        )}

        <p className="text-center mt-4 text-sm text-gray-600">
          Already have an account?{" "}
          <button
            type="button"
            onClick={() => navigate("/login")}
            className="text-blue-600 hover:underline"
          >
            Log in
          </button>
        </p>
      </form>
    </div>
  );
}
