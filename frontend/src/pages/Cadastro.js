import React, { useState } from "react";

function Cadastro() {
  const [isLogin, setIsLogin] = useState(true);

  const toggleMode = (e) => {
    e.preventDefault();
    setIsLogin(!isLogin);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(isLogin ? "Executando Sign In" : "Executando Sign Up");
  };

  return (
    <form className="container" onSubmit={handleSubmit}>
      <div className="image-section">
        <div className="overlay"></div>
      </div>
      <div className="form-section">
        <div className="form-container">
          <h1>{isLogin ? "Hello, Welcome Back!" : "Hello, Welcome!"}</h1>

          {isLogin ? (
            <>
              {" "}
              {/* Login */}
              <input type="text" placeholder="Username" required />
              <input type="password" placeholder="Password" required />
            </>
          ) : (
            <>
              {" "}
              {/* Cadastro */}
              <input type="text" placeholder="Username" required />
              <input type="email" placeholder="Email" required />
              <input type="password" placeholder="Password" required />
            </>
          )}

          <button type="submit">{isLogin ? "Sign In" : "Sign Up"}</button>

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
