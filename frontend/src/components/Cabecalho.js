import React from "react";
import { useNavigate } from "react-router-dom";

export default function Cabecalho() {
  const navigate = useNavigate();

  return (
    <header className="home-header">
      <h2 className="logo">AbraoAbrao</h2>
      <nav className="nav-buttons">
        <button onClick={() => navigate("/cadastro")}>Sign In</button>
        <button onClick={() => navigate("/cadastro")}>Sign Up</button>
      </nav>
    </header>
  );
}
