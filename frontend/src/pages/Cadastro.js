import React, { useState } from "react";
import { useLocation } from 'react-router-dom';

function Cadastro() {
  const location = useLocation();
  const [isLogin, setIsLogin] = useState(location.state?.isLogin ?? false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");  // Only used for signup
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const toggleMode = (e) => {
    e.preventDefault();
    setIsLogin(!isLogin);
    setMessage("");
    setUsername("");
    setEmail("");
    setPassword("");
};


  const handleSubmit = async (e) => {
    e.preventDefault();

    const url = isLogin
      ? "http://localhost:8000/signin"
      : "http://localhost:8000/signup";

    const payload = isLogin
      ? { email, password }
      : { name: username, email, password };

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok) {
        setMessage(`✅ Success! Welcome, ${data.user.name}`);
        console.log("User:", data.user);
      } else {
        setMessage(`❌ Error: ${data.detail || data.message}`);
        console.error("Error:", data);
      }
    } catch (error) {
      setMessage(`❌ Network error: ${error.message}`);
      console.error("Network error:", error);
    }
  };

  return (
    <form className="container" onSubmit={handleSubmit}>
      <div className="image-section">
        <div className="overlay"></div>
      </div>
      <div className="form-section">
        <div className="form-container">
          <h1>{isLogin ? "Hello, Welcome Back!" : "Hello, Welcome!"}</h1>

          {!isLogin && (
            <input
              type="text"
              placeholder="Username"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          )}
          <input
            type="email"
            placeholder="Email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button type="submit">{isLogin ? "Sign In" : "Sign Up"}</button>

          {message && <div className="message">{message}</div>}

          <div className="toggle">
            {isLogin ? (
              <span>
                Don't have an account?{" "}
                <a href="#" onClick={toggleMode}>
                  Sign Up
                </a>
              </span>
            ) : (
              <span>
                Already have an account?{" "}
                <a href="#" onClick={toggleMode}>
                  Sign In
                </a>
              </span>
            )}
          </div>
        </div>
      </div>
    </form>
  );
}

export default Cadastro;
